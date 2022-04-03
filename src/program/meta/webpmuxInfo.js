import {Program} from "../../Program.js";

export class webpmuxInfo extends Program
{
	website = "https://developers.google.com/speed/webp/download";
	package = "media-libs/libwebp";
	bin     = "webpmux";
	args    = r => ["-info", r.inFile()];
	post    = r =>
	{
		const meta = {};
		let seenFramesHeader = false;
		const frameSizes = [];
		const NUM_COLS = ["numberOfFrames"];
		r.stdout.trim().split("\n").filter(v => !!v).forEach(line =>
		{
			if(seenFramesHeader)
			{
				const cols = line.trim().innerTrim().split(" ").map(v => v.trim());
				frameSizes.push(+cols[9]);
			}
			else
			{
				const props = (line.trim().match(/^(?<name>[^:]+):\s+(?<val>.+)$/) || {})?.groups;
				if(!props)
					return;

				if(props.name==="No.")
				{
					seenFramesHeader = true;
					return;
				}

				const propKey = props.name.toCamelCase().replaceAll(" ", "").trim();
				meta[propKey] = NUM_COLS.includes(propKey) ? +props.val.trim() : props.val.trim();
			}
		});
		meta.frameSizesUnique = frameSizes.unique();

		Object.assign(r.meta, meta);
	};
	renameOut = false;
}
