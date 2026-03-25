import argparse
import logging
import socket
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Pose2D:
    x: float
    y: float
    rot_deg: float


T1_MOTORS = (
    "he1",
    "he2",
    "lae1",
    "lae2",
    "lae3",
    "lae4",
    "rae1",
    "rae2",
    "rae3",
    "rae4",
    "te1",
    "lle1",
    "lle2",
    "lle3",
    "lle4",
    "lle5",
    "lle6",
    "rle1",
    "rle2",
    "rle3",
    "rle4",
    "rle5",
    "rle6",
)

# Minimal static stand pose equivalent to passing's Neutral keyframe for T1.
T1_NEUTRAL_POS_DEG = {
    "lae2": -89.954,  # left shoulder roll
    "rae2": 89.954,   # right shoulder roll
}


class RcssServerMjClient:
    def __init__(self, host: str, port: int):
        self._host = host
        self._port = port
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    def connect(self) -> None:
        logger.info("Connecting to %s:%d", self._host, self._port)
        while True:
            try:
                self._sock.connect((self._host, self._port))
                break
            except ConnectionRefusedError:
                logger.warning("Connection refused; retrying...")
        logger.info("Connected.")

    def close(self) -> None:
        try:
            self._sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        self._sock.close()

    def send_cmd(self, cmd: str) -> None:
        payload = cmd.encode()
        self._sock.sendall(len(payload).to_bytes(4, byteorder="big") + payload)

    def recv_packet(self) -> str:
        header = self._recv_exact(4)
        msg_len = int.from_bytes(header, byteorder="big", signed=False)
        body = self._recv_exact(msg_len) if msg_len else b""
        return body.decode()

    def _recv_exact(self, n: int) -> bytes:
        buf = bytearray(n)
        view = memoryview(buf)
        received = 0
        while received < n:
            r = self._sock.recv_into(view[received:], n - received)
            if r == 0:
                raise ConnectionResetError("Socket closed by server")
            received += r
        return bytes(buf)


def _extract_playmode(gs_block: str) -> str | None:
    # Minimal parse for: (GS (pm BeforeKickOff) ...)
    key = "(pm "
    idx = gs_block.find(key)
    if idx < 0:
        return None
    start = idx + len(key)
    end = gs_block.find(")", start)
    if end < 0:
        return None
    return gs_block[start:end].strip()


def _extract_gs_block(packet: str) -> str | None:
    # Pull out the top-level "(GS ...)" s-expression block.
    tag = "(GS"
    start = packet.find(tag)
    if start < 0:
        return None
    depth = 0
    for i in range(start, len(packet)):
        if packet[i] == "(":
            depth += 1
        elif packet[i] == ")":
            depth -= 1
            if depth == 0:
                return packet[start : i + 1]
    return None


def _is_beam_allowed_playmode(playmode: str | None) -> bool:
    # Mirrors the practical behavior in passing/: beam during initial setup and after goals.
    return playmode in ("BeforeKickOff", "Goal_Left", "Goal_Right")


def _t1_neutral_pd_cmd(kp: float = 150.0, kd: float = 1.0) -> str:
    parts = []
    for motor in T1_MOTORS:
        q = T1_NEUTRAL_POS_DEG.get(motor, 0.0)
        parts.append(f"({motor} {q:.3f} 0.0 {kp:.3f} {kd:.3f} 0.0)")
    return "".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Minimal client: connect + init robot model + beam to fixed pose."
    )
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument("--port", type=int, default=60000)
    parser.add_argument("--team", type=str, default="Obstacles")
    parser.add_argument("--number", type=int, default=1)
    parser.add_argument("--model", type=str, default="T1", help="Robot model name (e.g., T1)")
    parser.add_argument("--x", type=float, required=True)
    parser.add_argument("--y", type=float, required=True)
    parser.add_argument("--rot", type=float, default=0.0, help="Rotation in degrees")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%H:%M:%S",
    )

    pose = Pose2D(x=args.x, y=args.y, rot_deg=args.rot)
    client = RcssServerMjClient(host=args.host, port=args.port)

    client.connect()

    # This is the minimum "load robot model" step from passing/: (init <model> <team> <number>)
    client.send_cmd(f"(init {args.model} {args.team} {args.number})")
    neutral_cmd = _t1_neutral_pd_cmd() if args.model == "T1" else ""

    try:
        while True:
            packet = client.recv_packet()
            gs = _extract_gs_block(packet)
            playmode = _extract_playmode(gs) if gs else None

            if _is_beam_allowed_playmode(playmode):
                client.send_cmd(f"(beam {pose.x} {pose.y} {pose.rot_deg})" + neutral_cmd)
            else:
                # Keep the client active with an explicit no-op action.
                client.send_cmd("(syn)" + neutral_cmd)
    finally:
        client.close()


if __name__ == "__main__":
    main()

