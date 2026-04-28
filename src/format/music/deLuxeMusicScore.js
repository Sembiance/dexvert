import {Format} from "../../Format.js";

export class deLuxeMusicScore extends Format
{
	name        = "DeLuxe Music Score";
	magic       = ["IFF Deluxe Music Score"];
	unsupported = true;	// only 6 unique files on discmaster
	notes       = "Likely from the Deluxe Music Construction Set";
}
