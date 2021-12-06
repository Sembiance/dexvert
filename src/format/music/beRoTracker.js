import {Format} from "../../Format.js";

export class beRoTracker extends Format
{
	name        = "BeRoTracker Module";
	ext         = [".brt"];
	magic       = ["BeRoTracker module"];
	unsupported = true;
	notes       = "A 32bit linux 1997 player in: sandbox/app/BeRoLinuxPlayer v1.0.rar  Could get an OLD linux OS and install in QEMU: https://soft.lafibre.info/";
}
