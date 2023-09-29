import {Format} from "../../Format.js";

export class synderSNG extends Format
{
	name        = "Synder SNG-Player Module";
	ext         = [".sng"];
	magic       = ["Synder SNG-Player module"];
	unsupported = true;
	notes       = "An old 3bit linux player binary can be found sandbox/app/Synder SNG-Player Linux32 build 2008-05-19.rar   Could get an OLD linux OS and install: https://soft.lafibre.info/";
}
