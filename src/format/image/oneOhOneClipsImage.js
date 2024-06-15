import {Format} from "../../Format.js";
import {path} from "std";

export async function _forceFormatByte({r})
{
	// Konvertor only understands the file if the 5th byte is 0x02, which is a screenshot. But other things like 0x03 are an image copy and if we convert it to 0x02 then Konvertor handles it ok
	// So we just always force the 5th byte to 0x02 to make Konvertor happy
	const buf = await Deno.readFile(r.f.input.absolute);
	buf[4] = 0x02;
	await Deno.writeFile(path.join(r.f.outDir.absolute, path.basename(r.f.input.absolute)), buf);
}

export class oneOhOneClipsImage extends Format
{
	name           = "101 Clips Image";
	website        = "https://archive.org/details/tucows_370916_101_Clips_Pro";
	ext            = [".img"];
	forbidExtMatch = true;
	magic          = [/^101 Clips Image$/];
	weakMagic      = true;
	converters     = ["callFunction[formatid:image/oneOhOneClipsImage][functionKey:_forceFormatByte] -> konvertor"];
}
