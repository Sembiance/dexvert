import {Format} from "../../Format.js";

export class thePlayer extends Format
{
	name         = "The Player Module";
	website      = "http://fileformats.archiveteam.org/wiki/The_Player";
	ext          = [".p61", ".p61a", ".p60", ".p60a", ".p50", ".p50a", ".p41", ".p40", "p40a", ".p40b", ".p30", "p30a", ".p22", ".p22a"];
	magic        = [/^The Player \d\.[01][ab] module$/, "The Player 4.x Music"];
	metaProvider = ["musicInfo"];
	converters   = ["xmp", "uade123[player:PTK-Prowiz]"];
}
