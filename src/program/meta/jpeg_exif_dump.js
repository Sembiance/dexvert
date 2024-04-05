import {Program} from "../../Program.js";

export class jpeg_exif_dump extends Program
{
	website = "https://github.com/nico/hack/blob/main/jpeg_exif_dump.c";
	package = "media-gfx/jpeg_exif_dump";
	bin     = "jpeg_exif_dump";
	args    = r => ["--scan", r.inFile()];
	post    = r =>
	{
		const meta = {};
		let driCount=0;
		r.stdout.trim().split("\n").forEach(line =>
		{
			const {driOffset} = line.match(/^ffdd at offset (?<driOffset>\d+), size 4/)?.groups || {};
			if(driOffset)
				meta.driOffset = +driOffset;

			if((/^ffd[0-7] at offset/).test(line))
				driCount++;
		});

		if(meta.driOffset)
			Object.assign(meta, {driCount});

		Object.assign(r.meta, meta);
	};
	renameOut = false;
}
