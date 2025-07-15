import {Format} from "../../Format.js";

export class huffmanCompressedAudio extends Format
{
	name           = "Huffman Compressed audio";
	ext            = [".hcom"];
	forbidExtMatch = true;
	magic          = ["Huffman Compressed audio", "soxi: hcom", /^Macintosh HCOM \(hcom\)$/];
	converters     = ["sox[type:hcom]"];
}
