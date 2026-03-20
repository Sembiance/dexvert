import {xu} from "xu";
import {Program} from "../../Program.js";
import {xmlParse} from "std";

export class jpeg_exif_dump extends Program
{
	website    = "https://github.com/nico/hack/blob/main/jpeg_exif_dump.c";
	package    = "media-gfx/jpeg_exif_dump";
	bin        = "jpeg_exif_dump";
	args       = r => ["--scan", r.inFile()];
	runOptions = {stdoutLimit : xu.KB*100};	// some files have MASSIVE amounts of metadata that we don't really care about. See samples: Neddy_Flyer_ft_HeatherRyan.jpg and skin.jpg
	post       = r =>
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

		if(r.stdout.includes("<x:xmpmeta"))
		{
			try
			{
				const NUMBER_KEYS = ["FullPanoWidthPixels", "FullPanoHeightPixels", "CroppedAreaImageWidthPixels", "CroppedAreaImageHeightPixels", "CroppedAreaLeftPixels", "CroppedAreaTopPixels", "InitialViewHeadingDegrees", "InitialViewPitchDegrees", "InitialHorizontalFOVDegrees"];
				const BOOL_KEYS = ["UsePanoramaViewer"];
				const xmlDoc = xmlParse(new RegExp(/<x:xmpmeta.*<\/x:xmpmeta>/, "s").exec(r.stdout)[0]);
				const rdf = xmlDoc.root.children.find(c => c.name?.raw === "rdf:RDF");
				const description = rdf.children.find(c => c.name?.raw === "rdf:Description");
				const gpano = {};

				for(const [key, value] of Object.entries(description.attributes))
				{
					if(key.startsWith("GPano:"))
					{
						const objKey = key.replace("GPano:", "");
						gpano[objKey] = NUMBER_KEYS.includes(objKey) ? +value : (BOOL_KEYS.includes(objKey) ? value.toLowerCase()==="true" : value);
					}
				}

				if(Object.keys(gpano).length)
					meta.gpano = gpano;
			}
			catch(err)
			{
				r.xlog.warn`jpeg_exif_dump failed to parse xmlData: ${err}`;
			}
		}

		if(meta.driOffset)
			Object.assign(meta, {driCount});

		Object.assign(r.meta, meta);
	};
	renameOut = false;
}
