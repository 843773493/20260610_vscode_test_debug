import os
import subprocess
import sys
import time
from collections.abc import Generator
from pathlib import Path

import pytest
import requests


def _kill_processes_listening_on_port(port: int) -> None:
	netstat = subprocess.run(
		["netstat", "-ano", "-p", "TCP"],
		check=False,
		capture_output=True,
		text=True,
	)
	if netstat.returncode != 0:
		return

	pids: set[int] = set()
	needle = f":{port}"
	for line in netstat.stdout.splitlines():
		if needle not in line or "LISTENING" not in line.upper():
			continue
		parts = line.split()
		if not parts:
			continue
		try:
			pids.add(int(parts[-1]))
		except ValueError:
			continue

	for pid in pids:
		subprocess.run(
			["taskkill", "/PID", str(pid), "/F"],
			check=False,
			capture_output=True,
			text=True,
		)


@pytest.fixture(scope="session", autouse=True)
def backend_server() -> Generator[None, None, None]:
	project_root = Path(__file__).resolve().parents[2]
	app_path = project_root / "app" / "main.py"
	debugpy_port = "5678"
	backend_port = 8000

	_kill_processes_listening_on_port(backend_port)
	_kill_processes_listening_on_port(int(debugpy_port))

	process = subprocess.Popen(
		[
			sys.executable,
			"-m",
			"debugpy",
			# "--wait-for-client",
			"--listen",
			f"127.0.0.1:{debugpy_port}",
			str(app_path),
		],
		cwd=project_root,
		env={**os.environ},
		stdout=subprocess.DEVNULL,
		stderr=subprocess.DEVNULL,
	)

	try:
		time.sleep(0.5)
		deadline = time.time() + 20
		while time.time() < deadline:
			try:
				response = requests.get("http://127.0.0.1:8000/health", timeout=1)
				if response.status_code == 200:
					break
			except requests.RequestException:
				pass
			time.sleep(0.2)
		else:
			raise RuntimeError("FastAPI backend did not become ready on port 8000")

		yield
	finally:
		process.terminate()
		try:
			process.wait(timeout=5)
		except subprocess.TimeoutExpired:
			process.kill()