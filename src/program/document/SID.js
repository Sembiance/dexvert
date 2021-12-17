import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class SID extends Program
{
	website  = "https://github.com/tylerapplebaum/setupinxhacking";
	loc      = "win2k";
	bin      = "c:\\dexvert\\SID\\sid.exe";
	unsafe   = true;
	args     = () => [];
	qemuData = r => ({
		script : `
			WinWaitActive("[sid] sexy installshield decompiler", "", 10)

			Sleep(500)
			Send("!f")
			Sleep(100)
			Send("o")
			Sleep(100)

			WinWaitActive("Choose file to decompile", "", 10)
			Sleep(200)
			Send("c:\\in\\${path.basename(r.inFile())}{ENTER}")
			WinWaitClose("Choose file to decompile", "", 10)

			Local $winHandle = WinGetHandle("[sid] sexy installshield decompiler")

			; Wait for the the progress bar to fill up
			Local $pixelColor
			Local $timer = TimerInit()
			Do
				$pixelColor = PixelGetColor(1015, 729, $winHandle)
				If Hex($pixelColor) == "00000080" Then ExitLoop
				Sleep(50)
			Until TimerDiff($timer) > ${xu.MINUTE*2}

			Sleep(${xu.SECOND*10})

			ClipPut("")
			Send("^a")
			Sleep(50)
			Send("^c")
			WaitForClipChange(${xu.SECOND})
			FileWrite("c:\\out\\out.txt", ClipGet())

			Sleep(500)
			Send("!f")
			Sleep(100)
			Send("q")
			Sleep(100)
			
			WinWaitClose("[sid] sexy installshield decompiler", "", 10)`
	});
	renameOut = true;
}
