import {xu} from "xu";
import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";
import {extractEXEOverlay} from "../../exeOverlayUtil.js";
import {fileUtil} from "xutil";
import {identify} from "../../identify.js";

let formats = null;

const SKIP_IDS = [
	// not useful
	"other/nullBytes",
	"other/nullBytesAlternating",

	// not trustworthy
	"text/txt"
];

export class exeOverlayID extends Program
{
	website = "https://github.com/Sembiance/dexvert/";
	loc     = "local";
	exec    = async r =>
	{
		if(!formats)
			({formats} = await import("../../format/formats.js"));

		r.meta.detections = [];

		const tmpFilePath = await fileUtil.genTempPath();
		await extractEXEOverlay(r.inFile({absolute : true}), tmpFilePath);
		if(!(await fileUtil.exists(tmpFilePath)))
			return;

		const {ids : identifications} = await identify(tmpFilePath, {xlog : r.xlog});
		for(const {from, matchType, family, formatid, confidence} of identifications)
		{
			if(from!=="dexvert" || matchType!=="magic")
				continue;

			const dexid = `${family}/${formatid}`;
			if(SKIP_IDS.includes(dexid))
				continue;

			const format = formats[formatid];
			r.meta.detections.push(Detection.create({value : `overlay: ${dexid}`, from : "exeOverlayID", weak : !!format.unsupported || confidence<20, confidence, file : r.f.input}));
		}

		const overlayIDs =
		[
			{id : "AS",      name : "Disk Express SFX", offset : 4},
			{id : "JRchive", name : "JRchive SFX"},
			{id : "KJd",     name : "RTPatch SFX"}
		];

		const overlayIDBuf = await fileUtil.readFileBytes(tmpFilePath, overlayIDs.map(o => o.id.length+(o.offset||0)).max());
		for(const {id, name, offset=0} of overlayIDs)
		{
			if(overlayIDBuf.length<(id.length+offset))
				continue;

			if(overlayIDBuf.getString(offset, id.length)===id)
				r.meta.detections.push(Detection.create({value : `overlay: ${name}`, from : "exeOverlayID", confidence : 100, file : r.f.input}));
		}


		await fileUtil.unlink(tmpFilePath);
	};
	renameOut = false;
}
