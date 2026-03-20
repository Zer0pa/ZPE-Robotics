from __future__ import annotations

import json
from pathlib import Path

from zpe_robotics.anomaly import inject_faults
from zpe_robotics.cli import main
from zpe_robotics.fixtures import generate_joint_trajectory
from zpe_robotics.lerobot_codec import build_synthetic_episode, dump_episode_json
from zpe_robotics.primitives import generate_primitive_corpus
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


def test_cli_supports_search_anomaly_lerobot_and_export_tokens(tmp_path: Path, capsys) -> None:
    codec = default_codec()

    library_dir = tmp_path / "library"
    library_dir.mkdir()
    library, _ = generate_primitive_corpus(seed=20260243, library_per_label=6, query_per_label=2, length=96)
    for idx, sample in enumerate(library):
        packet_path = library_dir / f"{sample.label}_{idx:03d}.zpbot"
        packet_path.write_bytes(codec.encode(sample.trajectory))

    assert main(["search", str(library_dir), "REACH"]) == 0
    search_output = json.loads(capsys.readouterr().out)
    assert search_output
    assert search_output[0]["matched_template"] == "REACH"

    fleet_dir = tmp_path / "fleet"
    fleet_dir.mkdir()
    for idx in range(4):
        nominal = generate_joint_trajectory(num_frames=512, num_joints=6, seed=400 + idx)
        (fleet_dir / f"nominal_{idx}.zpbot").write_bytes(codec.encode(nominal))
    base = generate_joint_trajectory(num_frames=512, num_joints=6, seed=500)
    anomalous, _ = inject_faults(base, seed=600)
    query_path = tmp_path / "query.zpbot"
    query_path.write_bytes(codec.encode(anomalous))
    assert main(["anomaly", str(fleet_dir), str(query_path)]) == 0
    anomaly_output = capsys.readouterr().out
    assert "z_score=" in anomaly_output

    dataset_dir = tmp_path / "lerobot_data"
    dataset_dir.mkdir()
    dump_episode_json(dataset_dir / "episode.json", build_synthetic_episode())
    output_dir = tmp_path / "compressed"
    assert main(["lerobot-compress", str(dataset_dir), str(output_dir)]) == 0
    compress_output = json.loads(capsys.readouterr().out)
    assert compress_output["files_processed"] == 1
    assert list(output_dir.rglob("*.zpbot"))

    packet_path = tmp_path / "tokens.zpbot"
    packet_path.write_bytes(codec.encode(generate_joint_trajectory(num_frames=128, num_joints=6, seed=700)))
    assert main(["export-tokens", str(packet_path), "--format", "fast"]) == 0
    token_output = json.loads(capsys.readouterr().out)
    assert token_output["format"] == "fast"
    assert token_output["authority_surface"] == "zpbot-v2"


def test_cli_generates_comm03_audit_bundle(tmp_path: Path, capsys) -> None:
    composition = build_single_packet_composition()
    packet_path = tmp_path / "canonical.zpbot"
    packet_path.write_bytes(composition.packet)
    output_dir = tmp_path / "comm03"

    assert main(["audit-bundle", str(packet_path), str(output_dir)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "PASS"
    assert (output_dir / "comm03_provenance_manifest.json").exists()
    assert (output_dir / "comm03_corruption_matrix.json").exists()
