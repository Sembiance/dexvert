import {Format} from "../../Format.js";

export class vic2Huffman extends Format
{
	name       = "Vic2 Huffman Compressed";
	magic      = ["Vic2: Huffman compressor with RLE", "Vice: Huffman compressor with RLE", "Archive: Huffman compressor with RLE (Vic2.)"];
	packed     = true;
	converters = ["ancient"];
}
