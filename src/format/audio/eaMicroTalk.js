import {Format} from "../../Format.js";

export class eaMicroTalk extends Format
{
	name         = "Electronic Arts MicroTalk";
	website      = "https://wiki.multimedia.cx/index.php/Electronic_Arts_MicroTalk";
	ext          = [".utk"];
	magic        = ["Maxis UTalk audio", "Maxis UTK (utk)"];
	metaProvider = ["ffprobe[libre]"];
	converters   = ["ffmpeg[libre][format:utk][outType:mp3]"];
}
