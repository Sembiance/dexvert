import {xu} from "xu";
import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class httpResponse extends Format
{
	name       = "HTTP Response";
	magic      = ["HTTP Response"];
	packed     = true;
	converters = async dexState =>
	{
		const buf = await fileUtil.readFileBytes(dexState.original.input.absolute, 1024);
		const dataSepLoc = buf.indexOfX("\r\n\r\n");
		if(dataSepLoc===-1)
			return [];

		return [`dd[skip:${dataSepLoc+4}]`];
	};
}
