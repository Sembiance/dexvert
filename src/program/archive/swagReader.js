import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class swagReader extends Program
{
	website = "http://fileformats.archiveteam.org/wiki/SWG";
	unsafe  = true;
	loc     = "dos";
	bin     = "SWAG/READER.EXE";
	args    = r => [`..\\..\\${r.inFile({backslash : true})}`];
	dosData = async r =>
	{
		const swagvR = await Program.runProgram("swagv", r.f.input, {xlog : r.xlog, autoUnlink : true});
		const dosKeys = [["Enter"]];
	
		r.pasFiles = swagvR.meta?.pasFiles;
		if(!r.pasFiles || r.pasFiles.length===0)
		{
			r.xlog.warn`Failed to find and pasFiles from swagv run ${swagvR.meta}`;
			return {timeout : xu.SECOND*10};
		}
		
		for(let i=0;i<r.pasFiles.length;i++)
		{
			dosKeys.push("E", `E:\\OUT\\${i}.PAS`, ["Enter"]);
			
			// Can add this delay and the one further below to help ensure the files get extracted under high system load
			//dosKeys.push({delay : 200});

			if((i+1)<r.pasFiles.length)
				dosKeys.push("N");	// , {delay : 250}
		}

		dosKeys.push(["Escape"], ["Escape"]);

		// Can take some time to run, thus the 10 minute timeout
		return {runIn : "prog", timeout : xu.MINUTE*10, keys : [{delay : xu.SECOND*5}, ...dosKeys]};
	};
	post = async r =>
	{
		await r.pasFiles.parallelMap(async (pasFile, i) =>
		{
			const outputFile = r.f.files.new.find(file => file.absolute===path.join(r.outDir({absolute : true}), `${i}.PAS`));
			if(outputFile)
			{
				await outputFile.rename(pasFile.filename);
				await outputFile.setTS(pasFile.ts);
			}
		});
	};
	renameOut = false;
}
