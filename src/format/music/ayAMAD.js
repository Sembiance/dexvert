import {xu} from "xu";
import {Format} from "../../Format.js";

export class ayAMAD extends Format
{
	name        = "AY Amadeus Chiptune";
	magic       = ["AY Amadeus chiptune"];
	ext         = [".amad"];
	unsupported = true;
	notes       = xu.trim`
		Ay_Emul can play these under linux, but they don't offer a command line conversion option. Source is available (delphi) so I could add support for this feature myself.
		zxtune123 doesn't seem to support them either.
		I tried several other programs like the AY To WAV converter here without luck: https://bulba.untergrund.net/progr_e.htm`;
}
