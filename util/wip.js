/* eslint-disable no-unused-vars */
import {xu, fg} from "xu";
import {XLog} from "xlog";
import {runUtil, fileUtil, printUtil, encodeUtil, cmdUtil} from "xutil";
import {path, delay, base64Encode} from "std";
import {Program} from "../src/Program.js";
import {formats, init as initFormats} from "../src/format/formats.js";
import {DexFile} from "../src/DexFile.js";
import {FileSet} from "../src/FileSet.js";
import {getDetections} from "../src/Detection.js";
import {programs, init as initPrograms} from "../src/program/programs.js";
import {UInt8ArrayReader} from "UInt8ArrayReader";

const xlog = new XLog("info");
//await initPrograms(xlog);
//await initFormats(xlog);

/*const {cb} = await runUtil.run("wine", ["c:\\dexvert\\DirectorCastRipper_D12/DirectorCastRipper.exe", "--files", "c:\\in77\\in.dir", "--output-folder", "c:\\out77", "--include-names", "--dismiss-dialogs"], {
	liveOutput : true,
	detached   : true,
	timeout    : 300_000,
	env        :
	{
		DISPLAY    : ":6365",
		WINEPREFIX : "/mnt/ram/dexvert/wine/base",
		WINEARCH   : "win32"
	}
});

const r = await cb();
xlog.info`${r}`;*/

//DISPLAY=:5347 WINEPREFIX=/mnt/ram/dexvert/wine/base WINARCH=win32 wine "c:\\dexvert\\DirectorCastRipper_D10/DirectorCastRipper.exe" 