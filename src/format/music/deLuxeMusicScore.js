import {Format} from "../../Format.js";

export class deLuxeMusicScore extends Format
{
	name        = "DeLuxe Music Score";
	magic       = ["IFF Deluxe Music Score"];
	unsupported = true;
	notes       = "Likely from the Deluxe Music Construction Set";
}
