import {xu} from "xu";
import {Format} from "../../Format.js";

export class gameCubeMusic extends Format
{
	name       = "GameCube Music";
	ext        = [".gcm"];
	magic      = ["GameCube Music (IDSP)", "Traveller's Tales IDSP (ttidsp)", "vgmstream: idsp_tt"];
	weakMagic  = true;
	converters = ["vgmstream[types:idsp_tt]", "zxtune123[strongMatch]"];
}
