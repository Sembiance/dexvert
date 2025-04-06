import {Format} from "../../Format.js";

export class gremlinDigitalVideo extends Format
{
	name         = "Gremlin Digital Video";
	website      = "https://wiki.multimedia.cx/index.php/Gremlin_Digital_Video";
	ext          = [".gdv"];
	magic        = ["Gremlin Digital Video"];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg", "nihav"];
}
