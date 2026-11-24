"""OBS で画面録画を始め・止める（play --obs）。

OBS 28 以降に入っている obs-websocket（v5）を使う。OBS の「ツール → WebSocket サーバー設定」で
サーバーを有効にし、パスワードを analysis/obs.json（{"password": "..."}。Git の管理外）か環境変数 OBS_PASSWORD に入れる。
ホストとポートの既定は localhost:4455（obs.json の "host"・"port" で変えられる）。

録画の開始時刻は、OBS が「録画が始まった」と返した瞬間の time.perf_counter()。
OBS の中で実際に最初のフレームを撮った時刻とは数十 ms ずれうる（未確認）。
"""

from __future__ import annotations

import json
import os
import shutil
import time
from pathlib import Path

ANALYSIS_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = ANALYSIS_DIR / "obs.json"


def load_config() -> dict:
    cfg = {"host": "localhost", "port": 4455, "password": ""}
    if CONFIG_PATH.exists():
        cfg.update(json.loads(CONFIG_PATH.read_text(encoding="utf-8")))
    cfg["password"] = os.environ.get("OBS_PASSWORD", cfg["password"])
    return cfg


class ObsRecorder:
    def __init__(self, client=None):
        if client is None:
            try:
                import obsws_python
            except ImportError as e:
                raise RuntimeError("obsws-python が入っていません。`pip install obsws-python` を流してください") from e
            cfg = load_config()
            try:
                client = obsws_python.ReqClient(host=cfg["host"], port=int(cfg["port"]),
                                                password=cfg["password"], timeout=5)
            except Exception as e:  # noqa: BLE001
                raise RuntimeError("OBS につながりません。OBS を起動し、WebSocket サーバーを有効にして、"
                                   f"パスワードを {CONFIG_PATH} か OBS_PASSWORD に入れてください（{e}）") from e
        self.cl = client
        self.t0: float | None = None

    def start(self, timeout: float = 5.0) -> float:
        if self.cl.get_record_status().output_active:
            raise RuntimeError("OBS がすでに録画中です。止めてからもう一度流してください")
        self.cl.start_record()
        end = time.perf_counter() + timeout
        while not self.cl.get_record_status().output_active:
            if time.perf_counter() > end:
                raise RuntimeError("OBS の録画が始まりません")
            time.sleep(0.01)
        self.t0 = time.perf_counter()
        return self.t0

    def stop(self, dest: Path | None = None) -> Path | None:
        """録画を止め、dest（拡張子なし）があればその名前で動かす。動かした先（か元の場所）を返す。"""
        out = self.cl.stop_record()
        src = Path(getattr(out, "output_path", "") or "")
        if not src.name:
            return None
        if dest is None:
            return src
        target = Path(dest).with_suffix(src.suffix)
        # OBS がファイルを閉じ終わるまで待つ
        for _ in range(50):
            try:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(target))
                return target
            except (PermissionError, FileNotFoundError):
                time.sleep(0.2)
        print(f"  [注意] 録画のファイルを動かせませんでした。元の場所にあります: {src}")
        return src
