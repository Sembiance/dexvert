import {Format} from "../../Format.js";

export class bethsoftVid extends Format
{
	name         = "Bethesda Softworks Video";
	website      = "https://wiki.multimedia.cx/index.php/Bethsoft_VID";
	ext          = [".vid"];
	magic        = ["Bethesda Softworks video", "Bethesda Softworks VID (bethsoftvid)"];
	metaProvider = ["ffprobe"];
	converters   = ["ffmpeg[format:bethsoftvid]"];
}
