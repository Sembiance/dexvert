<?php
foreach (glob(__DIR__ . '/P3TExtractor/*.php') as $f) require_once $f;
$p3t = new \P3TExtractor\Extractor($argv[1], $argv[2]);
$p3t->parse();
$p3t->dump_files("png,wav,jpg,p3t,gtf,jsx,edge,skel");
?>
