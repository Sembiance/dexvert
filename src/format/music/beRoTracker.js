import {Format} from "../../Format.js";

export class beRoTracker extends Format
{
	name           = "BeRoTracker Module";
	ext            = [".brt"];
	forbidExtMatch = true;
	magic          = ["BeRoTracker module"];
	weakMagic      = true;
	unsupported    = true;
	notes          = "A 32bit linux 1997 player in: sandbox/app/BeRoLinuxPlayer v1.0.rar  Could get an OLD linux OS emulated: https://soft.lafibre.info/";
}
