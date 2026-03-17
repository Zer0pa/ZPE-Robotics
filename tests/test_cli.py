from __future__ import annotations

from pathlib import Path

from zpe_robotics.cli import main
from zpe_robotics.release_candidate import build_single_packet_composition, default_codec
from zpe_robotics.rosbag_adapter import decode_records, encode_records


def test_cli_encode_verify_decode_and_info(tmp_path: Path) -> None:
    composition = build_single_packet_composition()
    bag_path = tmp_path / "input.bag"
    packet_path = tmp_path / "output.zpbot"
    replay_path = tmp_path / "replay.bag"

    bag_path.write_bytes(composition.bag_blob)

    assert main(["encode", str(bag_path), str(packet_path)]) == 0
    assert packet_path.exists()
    assert main(["verify", str(packet_path)]) == 0
    assert main(["info", str(packet_path)]) == 0
    assert main(["decode", str(packet_path), str(replay_path)]) == 0

    records = decode_records(replay_path.read_bytes(), default_codec(), decode_trajectory=True, strict_index=True)
    assert len(records) == 1
    assert records[0]["trajectory"].shape == composition.trajectory.shape


def test_cli_encode_rejects_multi_record_bag(tmp_path: Path) -> None:
    composition = build_single_packet_composition()
    multi_bag_path = tmp_path / "multi.bag"
    output_path = tmp_path / "output.zpbot"
    codec = default_codec()
    records = decode_records(composition.bag_blob, codec, decode_trajectory=True, strict_index=True)
    multi_blob = encode_records(records * 2, codec)
    multi_bag_path.write_bytes(multi_blob)

    assert main(["encode", str(multi_bag_path), str(output_path)]) == 1
