import {Format} from "../../Format.js";

export class neoDeskIcon extends Format
{
	name       = "NeoDesk Icon";
	website    = "http://fileformats.archiveteam.org/wiki/NeoDesk_icon";
	ext        = [".nic"];
	magic      = ["NeoDesk icon"];
	mimeType   = "image/x-neodesk-icon";
	converters = [`abydosconvert[format:${this.mimeType}]`];

	idCheck = (inputFile, detections) =>
	{
		// If we have a trid magic match, then we have a v3 file that starts with .NIC
		if(detections.some(detection => detection.value.startsWith("NeoDesk icon") && detection.from==="trid"))
			return true;

		// Otherwise we check to see if we have a v1 file that is 2088 bytes long or a v2 file which is a multiple of 244 bytes long
		return inputFile.size===2088 || inputFile.size%244===0;
	};
}
