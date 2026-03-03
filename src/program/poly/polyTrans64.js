import {xu} from "xu";
import {Program} from "../../Program.js";

const _FORMATS =
{
	cinema4D                  : {keys : "{DOWN}".repeat(10), importWindow : {title : "CINEMA 4D Import Plug-In", dismiss : "{ENTER}"}},
	collada                   : {keys : "{DOWN}".repeat(11), importWindow : {title : "Collada Geometry Import Plug-In Properties", dismiss : "{ENTER}"}},
	direct3DObject            : {keys : "{DOWN}".repeat(13), importWindow : {title : "DirectX Geometry Import Plug-In", dismiss : "o"}},
	dxf                       : {keys : "{DOWN}".repeat(16), importWindow : {title : "AutoCAD Geometry Import Plug-In", dismiss : "{ENTER}"}},
	electricImage3DFile       : {keys : "{DOWN}".repeat(17), importWindow : {title : "Electric Image FACT Geometry Import Plug-In", dismiss : "o"}},
	esriShape                 : {keys : "{DOWN}".repeat(18), importWindow : {title : "ESRI Shape File Geometry Import Plug-In", dismiss : "o"}},
	fbx5                      : {keys : "{DOWN}".repeat(19), importWindow : {title : "Okino's FBX v5.x (Kaydara SDK) Import Plug-In", dismiss : "o"}},
	fbx6                      : {keys : "{DOWN}".repeat(20), importWindow : {title : "Okino's FBX v6.x (2010.2) Import Plug-In", dismiss : "{ENTER}"}},
	fbx7                      : {keys : "{DOWN}".repeat(21), importWindow : {title : "Okino's FBX v7.x (2018.1) Import Plug-In", dismiss : "{ENTER}"}},
	industryFoundationClasses : {keys : "{DOWN}".repeat(25), importWindow : {title : "IFC (Industry Foundation Classes) Importer Properties", dismiss : "{ENTER}"}},
	lightWave                 : {keys : "{RIGHT}", importWindow : {title : "Lightwave Geometry Import Plug-In", dismiss : "{ENTER}"}},
	openInventor              : {keys : "{DOWN}".repeat(29), importWindow : {title : "Inventor2.x and VRML1 Geometry Import Plug-In", dismiss : "o"}},
	openNURBS                 : {keys : `{RIGHT}${"{DOWN}".repeat(11)}`, importWindow : [{title : "Rhino/OpenNURBS Geometry Importer Properties", dismiss : "{TAB}{TAB}{ENTER}"}, {title : "Info Request - NURBS Patch", dismiss : "y"}]},
	polygonFileFormat         : {keys : `{RIGHT}${"{DOWN}".repeat(5)}`, importWindow : {title : "PLY Geometry Import Plug-In", dismiss : "o"}},
	quickDraw3D               : {keys : `{RIGHT}${"{DOWN}".repeat(10)}`, importWindow : {title : "QuickDraw 3D Geometry Import Plug-In", dismiss : "o"}},
	sketchUp                  : {keys : `{RIGHT}${"{DOWN}".repeat(12)}`, importWindow : {title : "SketchUp 3D Geometry Import Plug-In", dismiss : "o"}},
	threeDStudio              : {keys : "{DOWN}".repeat(3), importWindow : {title : "3D Studio Geometry Import Plug-In", dismiss : "o"}},
	threeMF                   : {keys : "{DOWN}".repeat(5), importWindow : {title : "3D Manufacturing Format", dismiss : "{ENTER}"}},
	trueSpace3D               : {keys : `{RIGHT}${"{DOWN}".repeat(18)}`, importWindow : {title : "trueSpace Geometry Import Plug-In", dismiss : "o"}},
	universal3D               : {keys : `{RIGHT}${"{DOWN}".repeat(19)}`, importWindow : {title : "Universal-3D U3D Geometry Import Plug-In", dismiss : "o"}},
	usgsDEM                   : {keys : `{RIGHT}${"{DOWN}".repeat(21)}`, importWindow : {title : "USGS & GTOPO30 DEM v3.0 Geometry Import Plug-In", dismiss : "o"}},
	vrml1                     : {keys : `{RIGHT}${"{DOWN}".repeat(22)}`, importWindow : {title : "Inventor2.x and VRML1 Geometry Import Plug-In", dismiss : "o"}},
	vrml2                     : {keys : `{RIGHT}${"{DOWN}".repeat(23)}`, importWindow : {title : "VRML 2.0 Geometry Import Plug-In", dismiss : "o"}},
	x3d                       : {keys : `{RIGHT}${"{DOWN}".repeat(26)}`, importWindow : {title : "X3D and VRML2 Geometry Import Plug-In", dismiss : "o"}},
	xgl                       : {keys : `{RIGHT}${"{DOWN}".repeat(27)}`, importWindow : {title : "XGL Geometry Import Plug-In", dismiss : "o"}}
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
	loc     = "wine";
	bin     = "c:\\Program Files\\polytrans64\\pt64.exe";
	flags   = {
		format  : "Specify which format to import. REQUIRED",
		outType : "Specify which format to export to. REQUIRED"
	};
	args    = () => [];
	wineData  = r => ({
		base   : "win64",
		arch   : "win64",
		cwd    : "wine://Program Files/polytrans64",
		script : `
		WindowRequire("PolyTrans|CAD 3D Translation", "", 20)

		Sleep(500)

		Send("!")
		Sleep(500)
		Send("t")
		Sleep(500)
		Send("i")

		SendSlow("${_FORMATS[r.flags.format].keys}", 110)
		Send("{ENTER}")

		Func PreImportDialogs()
			WindowDismiss("Merge or Replace?", "", "{DOWN}{DOWN}{DOWN}{SPACE}{ENTER}")
			return WinActive("Select One or More Geometry Files to Import", "")
		EndFunc
		$importWindow = CallUntil("PreImportDialogs", ${xu.SECOND*30})
		If Not $importWindow Then
			Exit 0
		EndIf

		Sleep(500)
		SendSlow("c:\\in${r.wineCounter}\\${r.inFile()}{ENTER}", 75);
		WinWaitClose($importWindow, "", 100)

		Func PostImportDialogs()
			${_FORMATS[r.flags.format].importWindow ? Array.force(_FORMATS[r.flags.format].importWindow).map(o => `WindowDismiss("${o.title}", "", "${o.dismiss}")`).join("\n") : ``}
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
		$mainWindow = CallUntil("PostImportDialogs", ${xu.MINUTE*2})
		If Not $mainWindow Then
			Exit 0
		EndIf

		Send("!")
		Sleep(250)
		Send("t")
		Sleep(250)
		Send("e")

		SendSlow("${_OUT_TYPES[r.flags.outType || _OUT_TYPE_DEFAULT].keys}", 100)
		Send("{ENTER}")

		Func PreExportDialogs()
			WindowFailure("Warning", "no geometry to export", -1, "{ESCAPE}")
			$dismissed = WindowDismiss("${_OUT_TYPES[r.flags.outType || _OUT_TYPE_DEFAULT].exportWindow.title}", "", "${_OUT_TYPES[r.flags.outType || _OUT_TYPE_DEFAULT].exportWindow.keysDismiss}")
			$saveReady = WinActive("${_OUT_TYPES[r.flags.outType || _OUT_TYPE_DEFAULT].saveWindow.title}", "")
			return $dismissed Or $saveReady
		EndFunc
		CallUntil("PreExportDialogs", ${xu.SECOND*15})

		$saveWindow = WindowRequire("${_OUT_TYPES[r.flags.outType || _OUT_TYPE_DEFAULT].saveWindow.title}", "", 20)
		Sleep(250)
		SendSlow("c:\\out${r.wineCounter}\\out${_OUT_TYPES[r.flags.outType || _OUT_TYPE_DEFAULT].ext}{ENTER}", 85);
		WinWaitClose($saveWindow, "", 20)
		$outputStatusWindow = WinWaitActive("Geometry Export Status", "", 5)
		If $outputStatusWindow Then
			WinWaitClose($outputStatusWindow, "", 300)
		EndIf
		WaitForStableFileSize("c:\\out${r.wineCounter}\\out${_OUT_TYPES[r.flags.outType || _OUT_TYPE_DEFAULT].ext}", ${xu.SECOND*2}, ${xu.MINUTE*3.5})`,
		timeout : xu.MINUTE*23
	});
	renameOut = {
		alwaysRename : true,
		renamer      : [({r, fn, originalInput}) => (originalInput && fn===`out${_OUT_TYPES[r.flags.outType || _OUT_TYPE_DEFAULT].ext}` ? [originalInput.name, _OUT_TYPES[r.flags.outType || _OUT_TYPE_DEFAULT].ext] : [fn])]
	};
	chain = r => ((r.flags.outType || _OUT_TYPE_DEFAULT)==="glTF" ? null : `dexvert[asFormat:poly/${r.flags.outType || _OUT_TYPE_DEFAULT}]`);
}
