import {Format} from "../../Format.js";

export class fmTownsMovieVideo extends Format
{
	name           = "FM Towns Movie video";
	ext            = [".mov"];
	forbidExtMatch = true;
	magic          = ["FM Towns Movie video"];
	converters     = ["vibe2avi"];
}
