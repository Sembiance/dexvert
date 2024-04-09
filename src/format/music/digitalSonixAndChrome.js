import {xu} from "xu";
import {Format} from "../../Format.js";

export class digitalSonixAndChrome extends Format
{
	name         = "Digital Sonix and Chrome Module";
	ext          = [".dsc"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123[player:DigitalSonixChrome]"];
	verify       = ({meta}) => meta.duration>=xu.SECOND;
}
