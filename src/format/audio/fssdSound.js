import {xu} from "xu";
import {Format} from "../../Format.js";

export class fssdSound extends Format
{
	name       = "FSSD SoundEdit Mac Sound";
	magic      = ["Wii sound data"];
	idMeta     = ({macFileType}) => macFileType==="FSSD";		// Creators seen: JOSH, SFX!, FSSC
	converters = ["fssd2wav"];
}
