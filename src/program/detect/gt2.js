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
	args      = async r =>
	{
		// disktype gets confused by some filenames, especially if they have control characters, so rename first: https://discmaster.textfiles.com/view/42767/NatGeoPhoto_002.tar/0020272_Biologist%20Fumika%20Takahashi%20searches%20for%20the%20federally%20endangered%20vernal%20pool%20tadpole%20shrimp,%20Lepidurus%20packardi,%20at%20the%20Kesterson%20Unit%20of%20the%20San%20Luis%20National%20Wildlife%20Refuge.%0a%0aThese%20rare%20shrimp%20have.jpg
		// we do it in args because this is the first time we have access to r.wineData.wineCounter
		const wineBaseEnv = await (await fetch(`http://${WINE_WEB_HOST}:${WINE_WEB_PORT}/getBaseEnv`)).json();
		const gt2FilePath = await fileUtil.genTempPath(path.join(wineBaseEnv.base.WINEPREFIX, "drive_c", `in${r.wineCounter}`), r.f.input.ext || "");
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
		const matchValues = (r.status?.stdout || "").split("\n").map(line => line.match(/^3: (?<magic>.+)/)?.groups.magic).filter(v => !!v);
		r.meta.detections = (matchValues.length!==1 || !matchValues[0].length || matchValues[0].startsWith("Fehler:")) ? [] : [Detection.create({value : `${matchValues[0]}`, from : "gt2", file : r.f.input})];
	};
	renameOut = false;
}
