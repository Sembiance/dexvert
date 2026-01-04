import {Format} from "../../Format.js";

export class yamahaSMAF extends Format
{
	name           = "Yamaha Synthetic Music Mobile Application Format";
	website        = "https://lpcwiki.miraheze.org/wiki/Yamaha_SMAF";
	ext            = [".mmf"];
	forbidExtMatch = true;
	magic          = ["Yamaha SMAF", "application/vnd.smaf", /^fmt\/1178( |$)/];
	notes          = "OK, this uses smaf825 to dump the music info to JSON and then uses a 'barely passable' vibe coded mmf2mid converter along with a period appropriate sound font. It's better than nothing but FAR from good. See sandbox/app/SMAF3.06e.pdf for info.";
	converters     = ["smaf825 -> mmf2mid -> timidity[midiFont:Yamaha_MA2]"];
	//converters     = ["smaf825 -> mmf2vgm -> zxtune123"];
}
