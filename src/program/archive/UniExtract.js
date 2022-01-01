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

			ProcessWaitClose("UniExtract.exe", 5)

			; UniExtract uses a ton of sub-programs to do it's magic, any one of which can 'hang' and keep files locked, so let's kill all potential sub-programs
			KillAll("UniExtract.exe")
			KillAll("7z.exe")
			KillAll("arc.exe")
			KillAll("arj.exe")
			KillAll("AspackDie.exe")
			KillAll("bin2iso.exe")
			KillAll("BOOZ.EXE")
			KillAll("cdirip.exe")
			KillAll("clit.exe")
			KillAll("cmdTotal.exe")
			KillAll("E_WISE_W.EXE")
			KillAll("Expander.exe")
			KillAll("EXTRACT.EXE")
			KillAll("extractMHT.exe")
			KillAll("helpdeco.exe")
			KillAll("i3comp.exe")
			KillAll("i5comp.exe")
			KillAll("i6comp.exe")
			KillAll("innounp.exe")
			KillAll("IsXunpack.exe")
			KillAll("kgb_arch_decompress.exe")
			KillAll("lzop.exe")
			KillAll("MsiX.exe")
			KillAll("NBHextract.exe")
			KillAll("nrg2iso.exe")
			KillAll("pea.exe")
			KillAll("PEiD.exe")
			KillAll("RAIU.EXE")
			KillAll("STIX_D.EXE")
			KillAll("tee.exe")
			KillAll("trid.exe")
			KillAll("UHARC02.EXE")
			KillAll("UHARC04.EXE")
			KillAll("unlzx.exe")
			KillAll("UnRAR.exe")
			KillAll("UNUHARC06.EXE")
			KillAll("unzip.exe")
			KillAll("upx.exe")
			KillAll("uudeview.exe")
			KillAll("WDOSXLE.EXE")
			KillAll("WUN.EXE")
			KillAll("xace.exe")`
	});
	renameOut = false;
}
