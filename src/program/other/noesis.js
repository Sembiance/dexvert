import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

const _TYPE_OUT_SUFFIX =
{
	animated : "out.gif",
	archive  : "",
	image    : "out.png",
	poly     : "out.gltf"
};

const _TYPE_OUTPUT_FORMAT_KEYS =
{
	animated : `{HOME}${"{DOWN}".repeat(6)}`,
	archive  : "",
	image    : `{END}${"{UP}".repeat(4)}`,
	poly     : `{HOME}${"{DOWN}".repeat(3)}`
};

const _TYPE_CHAINS =
{
	animated : "ffmpeg[format:gif]",
	poly     : "?blender[format:gltf]"
};

export class noesis extends Program
{
	website = "https://richwhitehouse.com/index.php?content=inc_projects.php&showproject=91";
	flags   = {
		type : `Which type of input file: poly | animated  REQUIRED`
	};
	loc    = "win7";
	bin    = "c:\\dexvert\\noesisv4474\\Noesis64.exe";
	args   = r => [r.inFile()];
	osData = r => ({
		script : `
			Func WaitForFileToLoad()
				$statusBarText = WinGetText("Noesis")
				$statusBarTextTrimmed = StringStripWS($statusBarText, 7)
				return StringLen($statusBarTextTrimmed) > 0
			EndFunc
			CallUntil("WaitForFileToLoad", ${xu.SECOND*30})

			Func WaitForMainWindow()
				WindowDismiss("Open", "", "{ESCAPE}")
				return WinActive("Noesis", "")
			EndFunc
			$mainWindow = CallUntil("WaitForMainWindow", ${xu.SECOND*10})
			Sleep(250)

			Func WaitForExportWindow()
				Send("!f")
				Sleep(200)
				Send("e")

				WindowFailure("Noesis", "file type could not", -1, "{ENTER}")
				WindowFailure("Noesis", "No exportable files are selected", -1, "{ENTER}")

				return WinWaitActive("Export Media", "", 1)
			EndFunc
			$exportWindow = CallUntil("WaitForExportWindow", ${xu.SECOND*20})
			If Not $exportWindow Then
				Exit 0
			EndIf

			Send("{TAB}{TAB}{TAB}")
			Send("c:\\out\\${_TYPE_OUT_SUFFIX[r.flags.type]}")

			Send("{TAB}{TAB}")
			Send("${_TYPE_OUTPUT_FORMAT_KEYS[r.flags.type]}")

			Send("{ENTER}")

			Func WaitForExportComplete()
				WindowDismiss("Open", "", "{ESCAPE}")
				return WinActive("Noesis", "Export complete.")
			EndFunc
			$exportCompleteWindow = CallUntil("WaitForExportComplete", ${xu.MINUTE*2})
			Send("{ENTER}")
			WinWaitClose($exportCompleteWindow, "", 10)
			Send("{ESC}")
			WinWaitClose($exportWindow, "", 10)`
	});
	post = async r =>	// eslint-disable-line sembiance/shorter-arrow-funs
	{
		for(const newFile of r.f?.files?.new || [])
		{
			if(newFile.base===_TYPE_OUT_SUFFIX[r.flags.type])
				await newFile.rename(`${r.originalInput.name}${path.extname(_TYPE_OUT_SUFFIX[r.flags.type])}`);
		}
	};
	chain      = r => _TYPE_CHAINS[r.flags.type];
	chainCheck = (r, chainFile) =>
	{
		if(r.flags.type==="animated")
			return true;
		
		if(r.flags.type==="poly")
			return [".gltf"].includes(chainFile.ext.toLowerCase());
		
		return false;
	};
	chainPost = async r =>
	{
		if(r.flags.type!=="poly")
			return;

		const filesToRemove = [];
		for(const newFile of r.f?.files?.new || [])
		{
			if(newFile.ext!==".glb")
				filesToRemove.push(newFile);
		}
		for(const fileToRemove of filesToRemove)
			await r.f.remove("new", fileToRemove, {unlink : true});
	};
	renameOut = false;
}
