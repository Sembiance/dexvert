import {xu} from "xu";
import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";
import {path} from "std";
import {fileUtil} from "xutil";
import {WINE_WEB_HOST, WINE_WEB_PORT} from "../../wineUtil.js";

export class gt2 extends Program
{
	website = "https://www.helger.com/gt/gt2.htm";
	loc     = "wine";
	bin     = "c:\\Program Files\\GT2\\gt2.exe";
	args    = async r =>
	{
		// gt2 gets confused by some filenames (image/jpeg/0020272_*) and some extensions (executable/exe/el.-%0Aexit%0A), so rename first
		// we do it in args because this is the first time we have access to r.wineData.wineCounter
		const wineBaseEnv = await (await fetch(`http://${WINE_WEB_HOST}:${WINE_WEB_PORT}/getBaseEnv`)).json();
		const gt2FilePath = await fileUtil.genTempPath(path.join(wineBaseEnv.base.WINEPREFIX, "drive_c", `in${r.wineCounter}`), (r.f.input.ext || "").replaceAll(/[\t\n\r]/g, " "));
		await Deno.mkdir(path.dirname(gt2FilePath), {recursive : true});
		try
		{
			if(await fileUtil.exists(r.inFile({absolute : true})))
				await Deno.copyFile(r.inFile({absolute : true}), gt2FilePath);	// can't use a symlink as that changes the file type, hard link can't be used across different filesystems, so we have to copy. sad.
		}
		catch(err)
		{
			r.xlog.warn`Failed to copy file to tmp file for gt2: ${err}`;
		}

		return ["/noarcs", "/nu", "/noerrbox", "/nologo", "/nocolor", "/noscanname", "/noscanext", "/outlinenums", `c:\\in${r.wineCounter}\\${path.basename(gt2FilePath)}`];
	};
	
	// can't run more than 1 copy at a time, it messes up. Can test this by running this over and over: ./testdexvert --format=text/microsoftMapData
	// tried adding a preCopyDir feature (see sandbox/legacy/wineUtil-preCopyDir.js) where each instance is ran in it's own directory, but that didn't help, so it must be using like a common registry or something
	exclusive = "gt2";

	wineData  = {
		keepOutput : true,
		timeout    : xu.SECOND*2	// since we are only running 1 at a time, ensure it doesn't take took long to run and hang up everything else
	};
	post = r =>
	{
		// no need to delete the copied file, as it went into the 'in#' dir which wineUtil automatically deletes

		const matchValues = (r.status?.stdout || "").split("\n").map(line => line.match(/^3: (?<magic>.+)/)?.groups.magic).filter(v => !!v);
		r.meta.detections = (matchValues.length!==1 || !matchValues[0].length || matchValues[0].startsWith("Fehler:")) ? [] : [Detection.create({value : `${matchValues[0]}`, from : "gt2", file : r.f.input})];
	};
	renameOut = false;
}
