import {Format} from "../../Format.js";

export class westwoodStudiosVQA extends Format
{
	name         = "Westwood Studios Vector Quantized Animation";
	website      = "https://wiki.multimedia.cx/index.php/VQA";
	ext          = [".vqa"];
	magic        = ["Westwood VQA multimedia format", "Vector Quantized Animation video", "IFF data, Westwood Studios VQA Multimedia"];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg[format:wsvqa]"];
	notes        = "FFMPEG only has partial support. The HQ ones don't appear to be supported at all despite being documented out there. I tried VQA2AVI but that just produced black videos.";
}
