#encoding:utf-8
from cx_Freeze import setup,Executable

setup(
	name = "EDB",
	version = "1",
	description = "EDB F5 Steganography.",
	executables = [Executable("EDB.py")]
	)
