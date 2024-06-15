import {xu} from "xu";
import {Program} from "../../Program.js";

const _FORMATS =
{
	cinema4D                  : {keys : "{DOWN}".repeat(10), importWindow : {title : "CINEMA 4D Import Plug-In", keysDimiss : "{ENTER}"}},
	collada                   : {keys : "{DOWN}".repeat(11), importWindow : {title : "Collada Geometry Import Plug-In Properties", keysDimiss : "{ENTER}"}},
	direct3DObject            : {keys : "{DOWN}".repeat(13), importWindow : {title : "DirectX Geometry Import Plug-In", keysDimiss : "o"}},
	dxf                       : {keys : "{DOWN}".repeat(16), importWindow : {title : "AutoCAD Geometry Import Plug-In", keysDimiss : "{ENTER}"}},
	electricImage3DFile       : {keys : "{DOWN}".repeat(17), importWindow : {title : "Electric Image FACT Geometry Import Plug-In", keysDimiss : "o"}},
	esriShape                 : {keys : "{DOWN}".repeat(18), importWindow : {title : "ESRI Shape File Geometry Import Plug-In", keysDimiss : "o"}},
	fbx5                      : {keys : "{DOWN}".repeat(19), importWindow : {title : "Okino's FBX v5.x (Kaydara SDK) Import Plug-In", keysDimiss : "o"}},
	fbx6                      : {keys : "{DOWN}".repeat(20), importWindow : {title : "Okino's FBX v6.x (2010.2) Import Plug-In", keysDimiss : "{ENTER}"}},
	fbx7                      : {keys : "{DOWN}".repeat(21), importWindow : {title : "Okino's FBX v7.x (2018.1) Import Plug-In", keysDimiss : "{ENTER}"}},
	industryFoundationClasses : {keys : "{DOWN}".repeat(25), importWindow : {title : "IFC (Industry Foundation Classes) Importer Properties", keysDimiss : "{ENTER}"}},
	lightWave                 : {keys : "{RIGHT}", importWindow : {title : "Lightwave Geometry Import Plug-In", keysDimiss : "{ENTER}"}},
	openInventor              : {keys : "{DOWN}".repeat(29), importWindow : {title : "Inventor2.x and VRML1 Geometry Import Plug-In", keysDimiss : "o"}},
	openNURBS                 : {keys : `{RIGHT}${"{DOWN}".repeat(11)}`, importWindow : {title : "Rhino/OpenNURBS Geometry Importer Properties", keysDimiss : "{TAB}{TAB}{ENTER}"}},
	polygonFileFormat         : {keys : `{RIGHT}${"{DOWN}".repeat(5)}`, importWindow : {title : "PLY Geometry Import Plug-In", keysDimiss : "o"}},
	quickDraw3D               : {keys : `{RIGHT}${"{DOWN}".repeat(10)}`, importWindow : {title : "QuickDraw 3D Geometry Import Plug-In", keysDimiss : "o"}},
	sketchUp                  : {keys : `{RIGHT}${"{DOWN}".repeat(12)}`, importWindow : {title : "SketchUp 3D Geometry Import Plug-In", keysDimiss : "o"}},
	threeDStudio              : {keys : "{DOWN}".repeat(3), importWindow : {title : "3D Studio Geometry Import Plug-In", keysDimiss : "o"}},
	threeMF                   : {keys : "{DOWN}".repeat(5), importWindow : {title : "3D Manufacturing Format", keysDimiss : "{ENTER}"}},
	trueSpace3D               : {keys : `{RIGHT}${"{DOWN}".repeat(18)}`, importWindow : {title : "trueSpace Geometry Import Plug-In", keysDimiss : "o"}},
	universal3D               : {keys : `{RIGHT}${"{DOWN}".repeat(19)}`, importWindow : {title : "Universal-3D U3D Geometry Import Plug-In", keysDimiss : "o"}},
	usgsDEM                   : {keys : `{RIGHT}${"{DOWN}".repeat(21)}`, importWindow : {title : "USGS & GTOPO30 DEM v3.0 Geometry Import Plug-In", keysDimiss : "o"}},
	vrml1                     : {keys : `{RIGHT}${"{DOWN}".repeat(22)}`, importWindow : {title : "Inventor2.x and VRML1 Geometry Import Plug-In", keysDimiss : "o"}},
	vrml2                     : {keys : `{RIGHT}${"{DOWN}".repeat(23)}`, importWindow : {title : "VRML 2.0 Geometry Import Plug-In", keysDimiss : "o"}},
	x3d                       : {keys : `{RIGHT}${"{DOWN}".repeat(26)}`, importWindow : {title : "X3D and VRML2 Geometry Import Plug-In", keysDimiss : "o"}},
	xgl                       : {keys : `{RIGHT}${"{DOWN}".repeat(27)}`, importWindow : {title : "XGL Geometry Import Plug-In", keysDimiss : "o"}}
};

const _OUT_TYPES =
{
	glTF 	     : {keys : "{DOWN}".repeat(16), ext : ".glb", exportWindow : {title : "glTF 2.0 Exporter", keysDismiss : "{ENTER}}"}, saveWindow : {title : "Select the export filename"}},
	threeDStudio : {keys : "{DOWN}".repeat(4), ext : ".3ds", exportWindow : {title : "3D Studio Export Filter", keysDismiss : "o"}, saveWindow : {title : "Select Geometry Output Filename"}}
};
const _OUT_TYPE_DEFAULT = "glTF";

export class polyTrans64 extends Program
{
	website = "https://www.okino.com/conv/conv.htm";
	loc     = "win7";
	bin     = "c:\\Program Files\\PolyTrans64\\pt64.exe";
	flags   = {
		format  : "Specify which format to import. REQUIRED",
		outType : "Specify which format to export to. REQUIRED"
	};
	args    = () => [];
	osData  = r => ({
		cwd : "c:\\Program Files\\PolyTrans64",
		script : `
		WindowRequire("PolyTrans|CAD 3D Translation", "", 10)

		If Not FileExists("c:\\dexvert\\polyTrans64RanOnce.txt") Then
			FileWrite("c:\\dexvert\\polyTrans64RanOnce.txt", "yes")
			Sleep(2000)
		EndIf

		Send("!")
		Sleep(200)
		Send("t")
		Sleep(200)
		Send("i")

		SendSlow("${_FORMATS[r.flags.format].keys}", 50)
		Send("{ENTER}")

		Func PreImportDialogs()
			WindowDismiss("Merge or Replace?", "", "{DOWN}{DOWN}{DOWN}{SPACE}{ENTER}")
			return WinActive("Select One or More Geometry Files to Import", "")
		EndFunc
		$importWindow = CallUntil("PreImportDialogs", ${xu.SECOND*20})
		If Not $importWindow Then
			Exit 0
		EndIf

		Sleep(500)
		SendSlow("c:\\in\\${r.inFile()}{ENTER}", 50);
		WinWaitClose($importWindow, "", 60)

		Func PostImportDialogs()
			${_FORMATS[r.flags.format].importWindow ? `WindowDismiss("${_FORMATS[r.flags.format].importWindow.title}", "", "${_FORMATS[r.flags.format].importWindow.keysDimiss}")` : ``}
			WindowDismiss("Info Request", "Do you want to set the current animation length", "y")
			WindowDismiss("Info Request", "Resize the perspective camera", "n")
			WindowFailure("", "No valid polygons were found in the file", -1, "{ESCAPE}")
			WindowFailure("", "file import aborted.", -1, "{ESCAPE}")
			WindowFailure("", "Error while importing", -1, "{ESCAPE}")
			WindowFailure("", ". Aborting.", -1, "{ESCAPE}")
			WindowFailure("", "This is not supported, only the binary format", -1, "{ESCAPE}")
			WindowFailure("", "Could not read data from", -1, "{ESCAPE}")
			WindowFailure("", "is not in the X3D or VRML97 format", -1, "{ESCAPE}")
			WindowFailure("", "Error enumerating data objects", -1, "{ESCAPE}")
			WindowFailure("", "version number is not recognized", -1, "{ESCAPE}")
			WindowFailure("", "premature end of file", -1, "{ESCAPE}")
			WindowFailure("", "is not in the ", -1, "{ESCAPE}")
			WindowFailure("", "The file cannot be loaded", -1, "{ESCAPE}")
			WindowFailure("", "Could not locate or open", -1, "{ESCAPE}")
			WindowFailure("", "The input file is either not", -1, "{ESCAPE}")
			WindowFailure("", "cannot be parsed.", -1, "{ESCAPE}")
			return WinActive("PolyTrans|CAD 3D Translation, Viewing & Composition System - ", "")
		EndFunc
		$mainWindow = CallUntil("PostImportDialogs", ${xu.MINUTE*1.5})
		If Not $mainWindow Then
			Exit 0
		EndIf

		Send("!")
		Sleep(200)
		Send("t")
		Sleep(200)
		Send("e")

		Send("${_OUT_TYPES[r.flags.outType || _OUT_TYPE_DEFAULT].keys}")
		Send("{ENTER}")

		Func PreExportDialogs()
			WindowFailure("Warning", "no geometry to export", -1, "{ESCAPE}")
			return WindowDismiss("${_OUT_TYPES[r.flags.outType || _OUT_TYPE_DEFAULT].exportWindow.title}", "", "${_OUT_TYPES[r.flags.outType || _OUT_TYPE_DEFAULT].exportWindow.keysDismiss}")
		EndFunc
		CallUntil("PreExportDialogs", ${xu.SECOND*10})

		$saveWindow = WindowRequire("${_OUT_TYPES[r.flags.outType || _OUT_TYPE_DEFAULT].saveWindow.title}", "", 10)
		SendSlow("c:\\out\\out${_OUT_TYPES[r.flags.outType || _OUT_TYPE_DEFAULT].ext}{ENTER}", 50);
		WinWaitClose($saveWindow, "", 20)
		$outputStatusWindow = WinWaitActive("Geometry Export Status", "", 4)
		If $outputStatusWindow Then
			WinWaitClose($outputStatusWindow, "", 240)
		EndIf
		WaitForStableFileSize("c:\\out\\out${_OUT_TYPES[r.flags.outType || _OUT_TYPE_DEFAULT].ext}", ${xu.SECOND*2}, ${xu.MINUTE*3})`,
		timeout : xu.MINUTE*5
	});
	renameOut = {
		alwaysRename : true,
		renamer      : [({r, fn, originalInput}) => (originalInput && fn===`out${_OUT_TYPES[r.flags.outType || _OUT_TYPE_DEFAULT].ext}` ? [originalInput.name, _OUT_TYPES[r.flags.outType || _OUT_TYPE_DEFAULT].ext] : [fn])]
	};
	chain = r => ((r.flags.outType || _OUT_TYPE_DEFAULT)==="glTF" ? null : `dexvert[asFormat:poly/${r.flags.outType || _OUT_TYPE_DEFAULT}]`);
}
