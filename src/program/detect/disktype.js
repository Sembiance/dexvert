import {xu} from "xu";
import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";
import {fileUtil} from "xutil";

export class disktype extends Program
{
	website = "http://disktype.sourceforge.net";
	package = "sys-block/disktype";
	bin     = "disktype";
	loc     = "local";
	pre     = async r =>
	{
		// disktype gets confused by some filenames, especially if they have control characters, so rename first: https://discmaster.textfiles.com/view/42767/NatGeoPhoto_002.tar/0020272_Biologist%20Fumika%20Takahashi%20searches%20for%20the%20federally%20endangered%20vernal%20pool%20tadpole%20shrimp,%20Lepidurus%20packardi,%20at%20the%20Kesterson%20Unit%20of%20the%20San%20Luis%20National%20Wildlife%20Refuge.%0a%0aThese%20rare%20shrimp%20have.jpg
		r.disktypeFilePath = await fileUtil.genTempPath(undefined, r.f.input.ext || "");
		try
		{
			if(await fileUtil.exists(r.inFile({absolute : true})))
				await Deno.copyFile(r.inFile({absolute : true}), r.disktypeFilePath);			// can't use a symlink as that changes the file type, hard link can't be used across different filesystems, so we have to copy. sad.
		}
		catch(err)
		{
			r.xlog.warn`Failed to copy file to tmp file for disktype: ${err}`;
		}
	};
	args = r => [r.disktypeFilePath];
	post = async r =>
	{
		await fileUtil.unlink(r.disktypeFilePath);

		r.meta.detections = [];

		const magic = [];
		for(const line of r.stdout.trim().split("\n"))
		{
			if(["---", "Regular file", "Block device", "Character device", "FIFO", "Socket", "Unknown kind"].some(v => line.startsWith(v)))
				continue;

			if(line.trim().length)
				magic.push(line.trim());
		}

		if(magic.length)
			r.meta.detections.push(Detection.create({value : magic.join(" "), confidence : 100, from : "disktype", file : r.f.input}));
	};
	renameOut = false;
}
