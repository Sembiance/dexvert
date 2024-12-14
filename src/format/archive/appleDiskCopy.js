import {Format} from "../../Format.js";
import {flexMatch} from "../../identify.js";

const _APPLE_DISK_COPY_MAGIC = ["Apple DiskCopy", "DiskCopy ", /^fmt\/625( |$)/];
export {_APPLE_DISK_COPY_MAGIC};

export class appleDiskCopy extends Format
{
	name       = "Apple DiskCopy";
	website    = "https://www.discferret.com/wiki/Apple_DiskCopy_4.2";
	magic      = _APPLE_DISK_COPY_MAGIC;
	weakMagic  = [/^fmt\/625( |$)/];
	idMeta     = ({macFileType, macFileCreator}) => (["dImg", "dimg"].includes(macFileType) && ["dCpy", "Wrap"].includes(macFileCreator));
	idCheck    = (inputFile, detections, {idMetaMatch, xlog}) =>
	{
		// only return true if we have 2 or more detections against our magic or if we have just 1 match but it's not weak
		const validMagicDetections = detections.filter(detection => _APPLE_DISK_COPY_MAGIC.some(matchAgainst => flexMatch(detection.value, matchAgainst)));
		return (validMagicDetections.length+(idMetaMatch ? 1 : 0))>1 || (validMagicDetections.length===1 ? !validMagicDetections[0].weak : false);
	};
	converters = ["dd[bs:84][skip:1] -> dexvert[skipVerify][bulkCopyOut]", "IsoBuster"];
}
