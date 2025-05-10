import {Format} from "../../Format.js";
import {UInt8ArrayReader} from "UInt8ArrayReader";

export class vcomp extends Format
{
	name           = "Blaster Master VOC Compiled Audio";
	website        = "http://fileformats.archiveteam.org/wiki/VCOMP_(Blaster_Master)";
	ext            = [".exe"];
	forbidExtMatch = true;
	magic          = ["16bit DOS Blaster Master VOC Compiler Executable"];
	pre            = async dexState =>
	{
		const reader = new UInt8ArrayReader(await Deno.readFile(dexState.f.input.absolute), {endianness : "le"});
		reader.skip(2);
		const lastPageBytes = reader.uint16();
		const numPages = reader.uint16();
		dexState.meta.overlayOffset = ((numPages-1)*512)+(lastPageBytes || 512);
	};
	converters = dexState => [`dd[bs:${dexState.meta.overlayOffset}][skip:1] -> dexvert[asFormat:audio/voc]`];
}
