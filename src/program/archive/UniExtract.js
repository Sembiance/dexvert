import {Program} from "../../Program.js";

export class UniExtract extends Program
{
	website = "https://www.legroom.net/software/uniextract";
	flags   = {
		type : `Which type of extraction to choose. Examples: "i3comp extraction" or "STIX extraction"`
	};
	loc      = "win2k";
	bin      = "c:\\dexvert\\uniextract161\\UniExtract.exe";
	args     = r => [r.inFile()];
	qemuData = r => ({
		// UniExtract uses a ton of sub-programs to do it's magic, any one of which can 'hang' and keep files locked, so let's kill all potential sub-programs
		alsoKill : ["UniExtract.exe", "7z.exe", "arc.exe", "arj.exe", "AspackDie.exe", "bin2iso.exe", "BOOZ.EXE", "cdirip.exe", "clit.exe", "cmdTotal.exe", "E_WISE_W.EXE", "Expander.exe", "EXTRACT.EXE", "extractMHT.exe",
			"helpdeco.exe", "i3comp.exe", "i5comp.exe", "i6comp.exe", "innounp.exe", "IsXunpack.exe", "kgb_arch_decompress.exe", "lzop.exe", "MsiX.exe", "NBHextract.exe", "nrg2iso.exe", "pea.exe", "PEiD.exe",
			"RAIU.EXE", "STIX_D.EXE", "tee.exe", "trid.exe", "UHARC02.EXE", "UHARC04.EXE", "unlzx.exe", "UnRAR.exe", "UNUHARC06.EXE", "unzip.exe", "upx.exe", "uudeview.exe", "WDOSXLE.EXE", "WUN.EXE", "xace.exe"],
		script : `
			Local $mainWindow = WinWaitActive("Universal Extractor", "", 10)

			ControlSetText("Universal Extractor", "", "[CLASS:Edit; INSTANCE:2]", "c:\\out\\")
			Sleep(200)

			ControlClick("Universal Extractor", "", "[CLASS:Button; TEXT:&OK]")

			WinWaitClose($mainWindow, "", 10)

			Local $decisionWindow = WinWaitActive("Universal Extractor", "", 5)
			If $decisionWindow Then
				${r.flags.type ? `ControlClick("Universal Extractor", "", "[CLASS:Button; TEXT:${r.flags.type}]")` : ""}
				ControlClick("Universal Extractor", "", "[CLASS:Button; TEXT:&OK]")
			EndIf

			Local $hasError = WinWaitActive("Universal Extractor", "could not be extracted", 5)
			If $hasError Then
				ControlClick("Universal Extractor", "", "[CLASS:Button; TEXT:&Cancel]")
			EndIf

			WinWaitClose("Universal Extractor", "", 10)

			ProcessWaitClose("UniExtract.exe", 5)`
	});
	renameOut = false;
}
