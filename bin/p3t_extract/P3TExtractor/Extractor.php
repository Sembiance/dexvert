<?php
/**
 * Initiates the extraction process and read the P3T/RAF file
 * @package PS3Theme.net
 * @subpackage P3T Extractor
 * @access public
 * @author Hoshang Sadiq
 * @copyright 2011
 *
 * @changelog
 * @version 1.3.1
 * @date 07/05/2011
 * @fixed Now doesn't require the offset of the first element
 *
 * @changelog
 * @version 1.3
 * @date 06/05/2011
 * @new Now allows for selection of WAVE files
 * @new changed default save options to 'png,wav,jpg,p3t'
 * @new Now returns an array of features and if they are supported by the theme
 *      Currently this is only dynamic and audio
 * @new now tells more about what is happening at the moment
 *
 * @version 1.2.1
 * @date 04/01/2011
 * @fixed New header unpack format was errorous, reverted back to original
 *
 * @changelog
 * @version 1.2
 * @date 25/04/2011
 * @new Merged dump_xml() and dump_files()
 * @new dump_xml takes a list of file types to dump as an argument
 *
 * @changelog
 * @version 1.1
 * @date 13/02/2011
 * @new Option to provide the root folder
 * @new Option to echo what is currently happening
 * @new Option to save the XML
 * @fixed Elements getting wrong offset
 *
 * @changelog
 * @version 1.0
 * @date 23/01/2011
 */

namespace P3TExtractor;

class Extractor
{
    /**
     * Contains the location of the P3T/RAF file
     * @access private
     * @var string
     */
    private $filename;

    /**
     * Contains an array of elements extracted from the file.
     * These will be of Element type
     * @access private
     * @var array(Element)
     */
    private $elemap;

    /**
     * Contains the extraction root for the files
     * @access private
     * @var string
     */
    private $root;

    /**
     * Contains the P3T/RAF file's header information
     * @access private
     * @var Header
     */
    private $h;

    /**
     * Tells the script whether to echo status of the extraction or not
     * @access private
     * @var boolean
     */
    private $echo = false;

    /**
     * Construct the class
     * @param string $file Location of the P3T/RAF
     * @param string $root Extraction folder, if it doesn't exists, attempts to create it
     * @param bool $echo Whether or not to echo what the extractor is doing
     */
    public function __construct($file, $root, $echo = false)
    {
        $this->filename = $file;
        if (substr($root, -1) !== '/') {
            $root .= '/';
        }

        $this->root = $root;
        $this->echo = $echo;
    }

    /**
     * Parse the P3T/RAF file
     */
    public function parse()
    {
        // Create a ne P3T header
        $this->h = new Header($this->echo);

        if (pathinfo($this->filename, PATHINFO_EXTENSION) === 'p3t') {
            $this->h->custom('Opening file: ');
        }
        try {
            $f = fopen($this->filename, 'rb'); // Open P3T/RAF file
            if (pathinfo($this->filename, PATHINFO_EXTENSION) === 'p3t') {
                $this->h->success();
            }
        } catch (\Exception $e) {
            if (pathinfo($this->filename, PATHINFO_EXTENSION) === 'p3t') {
                $this->h->failed();
            }
            echo $e->getMessage();
            exit;
        }

        if (pathinfo($this->filename, PATHINFO_EXTENSION) === 'p3t') {
            $this->h->custom('Extracting header information: ');
        }
        try {
            // Read header, unpack header data, populate Header
            $header_bin = fread($f, 64); // Header size
            list($this->h->magic, $this->h->version, $this->h->tree_offset, $this->h->tree_size,
                $this->h->idtable_offset, $this->h->idtable_size, $this->h->stringtable_offset,
                $this->h->stringtable_size, $this->h->intarray_offset, $this->h->intarray_size,
                $this->h->floatarray_offset, $this->h->floatarray_size, $this->h->filetable_offset,
                $this->h->filetable_size) = unpack('a4h/N13i/x8f', $header_bin);
            // Header format
            if ($this->h->magic === 'P3TF') {
                $this->h->success();
            }
        } catch (\Exception $e) {
            if (pathinfo($this->filename, PATHINFO_EXTENSION) === 'p3t') {
                $this->h->failed();
            }
            echo $e->getMessage();
            exit;
        }

        // load string table
        fseek($f, $this->h->tree_offset);

        // read and save the elements and their attributes
        if ($this->h->magic === 'P3TF') {
            $this->h->custom('Finding elements and attributes: ');
        }
        try {
            while ((ftell($f) - $this->h->tree_offset) < $this->h->tree_size) {
                $ele = new Element($this->h);
                $ele->parse(fread($f, 28), 'N7', $f); // 28 = element size, N7 = element format

                // loop through attributes
                for ($y = 0; $y < $ele->numattr; $y++) {
                    $attr_bin = fread($f, 16); // attribute size
                    $attr = new Attribute();
                    $attr->parse($attr_bin, $this->h, $f);
                    $ele->setAttribute($attr);
                }

                // add current element to the list
                $this->elemap[$ele->offset] = $ele;
            }
            if ($this->h->magic === 'P3TF') {
                $this->h->success();
            }
        } catch (\Exception $e) {
            if ($this->h->magic === 'P3TF') {
                $this->h->failed();
            }
            echo $e->getMessage();
            exit;
        }

        // Assign all elements to their parents
        if ($this->h->magic === 'P3TF') {
            $this->h->custom('Reordering elements: ');
        }
        try {
            foreach ($this->elemap as $k => $v) {
                // ignore top parent element
                if ($v->parentoffset === -1) {
                    continue;
                }
                // add element to parent element
                if (isset($this->elemap[$v->parentoffset]) && $v->parentoffset != $k) {
                    /** @var Element $element */
                    $element = $this->elemap[$v->parentoffset];
                    $element->appendChild($v);
                }
            }

            // remove all but top most element
            $el = $this->elemap[0];
            $this->elemap = array($el);
            if ($this->h->magic === 'P3TF') {
                $this->h->success();
            }
        } catch (\Exception $e) {
            if ($this->h->magic === 'P3TF') {
                $this->h->failed();
            }
            echo $e->getMessage();
            exit;
        }

        if ($this->h->magic === 'P3TF') {
            $this->h->custom('Closing file: ');
        }
        try {
            fclose($f); // Close the file
            if ($this->h->magic === 'P3TF') {
                $this->h->success();
            }
        } catch (\Exception $e) {
            if ($this->h->magic === 'P3TF') {
                $this->h->failed();
            }
            echo $e->getMessage();
            exit;
        }
        if ($this->h->magic === 'P3TF') {
            $this->h->custom("\n\n");
        }
    }

    /**
     * Dump selected file types
     * @param string|array|bool $save A list of file types to save, this can be passed in several ways. This argument is case insensitive.
     *                                Boolean: If true, all files are extracted, if false, no files are dumped
     *
     *                                String: A string of file types to save, this can be delimited, but is not
     *                                        necessary, but it is recommended to delimit. If a file type is not present,
     *                                        the file will not be extracted. For a list of file types, see below.
     *                                        This method can also be '*' to set everything to true.
     *
     *                                Array: a array of file types to dump, can be a 1D or 2D. If a file type is not present,
     *                                       the file will not be extracted. For a list of file types, see below
     *
     *                                Default option: 'png,wav,jpg,p3t'
     *
     *                                File types:
     *                                 * GIM  - The original file type an icon is saved as within the P3T file
     *                                 * PNG  - Converts a GIM file to PNG and saves this file.
     *                                          Note: this dramatically slows the extractor down
     *                                 * JPG  - Static background images for a theme
     *                                 * VAG  - XMB Navigation audio files
     *                                 * WAV  - XMB Navigation converted to WAVE format
     *                                 * XML  - Extract XML files to be fed into the compiler, and it should compile
     *                                          properly. If set to true, this overrides both the P3T file type and RAF
     *                                 * P3T  - An XML file generated of the original P3T theme. Feeding this into the
     *                                          compiler, should compile properly. This automatically defaults to true
     *                                          if XML is true.
     *                                 * RAF  - An XML file generated by the RAF file for dynamic themes. This automatically
     *                                          defaults to true if XML is true.
     *                                 * GTF  - Texture files (.dds files optimised for Cell CPU). This contains the
     *                                          background image for dynamic themes
     *                                 * JSX  - Unknown what this is for
     *                                 * EDGE - Used for rendering frame borders
     *                                 * SKEL - Skeleton files
     * @return array
     * @throws \Exception
     */
    public function dump_files($save = 'png,wav,jpg,p3t')
    {
        if (!is_string($save) && !is_bool($save) && !is_array($save)) {
            throw new \Exception('Extractor::dump_files() -> argument 1 must be a boolean, string or array');
        }

        if ($this->h->magic === 'P3TF') {
            $this->h->custom('Determine which file types need to be saved: ');
        }
        try {
            // if save is *, save everything
            if ($save === '*') {
                $save = true;
            }

            // default settings, nothing is saved
            $default = array(
                'gim' => false,
                'png' => false,
                'jpg' => false,
                'vag' => false,
                'wav' => false,
                'p3t' => false,
                'raf' => false,
                'gtf' => false,
                'jsx' => false,
                'edge' => false,
                'skel' => false,
                'xml' => false
            );

            // determine which file types have been passed, update the options
            if (is_string($save)) {
                $save = strtolower($save);
                foreach ($default as $k => $v) {
                    $default[$k] = stripos($save, $k) !== false;
                }
            } else {
                if (is_bool($save)) {
                    foreach ($default as $k => $v) {
                        $default[$k] = $save;
                    }
                } else {
                    if (is_array($save)) {
                        $temp = array_keys($save);
                        if (is_int($temp[0])) {
                            $save = array_map('strtolower', $save);
                            foreach ($default as $k => $v) {
                                $default[$k] = in_array($k, $save, true);
                            }
                        } else {
                            $default = array_merge($default, $save);
                        }
                        unset($temp);
                    }
                }
            }
            if ($this->h->magic === 'P3TF') {
                $this->h->success();
            }
        } catch (\Exception $e) {
            if ($this->h->magic === 'P3TF') {
                $this->h->failed();
            }
            echo $e->getMessage();
            exit;
        }

        // cleanup
        $save = $default;
        unset($default);

        // override XML rule, if XML file type is true, both P3T and RAF are true
        if ($save['xml'] === true) {
            $save['p3t'] = true;
            $save['raf'] = true;
        }
        unset($save['xml']);
        if ($this->h->magic === 'P3TF') {
            $this->h->custom('Files to be saved: ' . "\n");
            foreach ($save as $format => $option) {
                $this->h->custom('    ' . $format . ': ' . ($option === true ? 'yes' : 'no') . "\n");
            }

            $this->h->custom("\n" . 'Extracting theme files. Sit back and relax.' . "\n\n");
        }

        // open the P3T/RAF file
        $f = fopen($this->filename, 'rb');
        /** @var Element $root_element */
        $root_element = $this->elemap[0];

        // recursively call dump_files from the root element
        $support = $root_element->dump_files($this->root, $f, $this->echo, $save);
        fclose($f); // close file

        // define the XML filename
        if ($this->h->magic === 'RAFO') {
            $file = $this->root . 'raf.xml';
        } else {
            $file = $this->root . 'p3t.xml';
        }

        $this->h->write($file);
        // Dump the p3t.xml or raf.xml
        if (($this->h->magic === 'RAFO' && $save['raf']) || ($this->h->magic === 'P3TF' && $save['p3t'])) {
            try {
                $doc = new \DOMDocument('1.0');
                $doc->formatOutput = true;
                $root_element->saveXML($doc);
                $doc->save($file);
                $this->h->success();
            } catch (\Exception $e) {
                $this->h->failed();
                echo $e->getMessage();
            }
        } else {
            $this->h->ignored();
        }


        if ($this->h->magic === 'P3TF') {
            $this->h->custom("\n\n" . 'Finished the extraction, found the following features:' . "\n");
            $this->h->custom('Dynamic support: ' . ($support['dynamic'] === true ? 'yes' : 'no') . "\n");
            $this->h->custom('Sound support: ' . ($support['audio'] === true ? 'yes' : 'no') . "\n");
        }

        return $support;
    }
}

/**
 * (PHP 4, PHP 5)<br/>
 * Unpack data from binary string with an indexed array
 * @link http://php.net/manual/en/function.unpack.php
 * @param string $format <p>
 * See pack for an explanation of the format codes.
 * </p>
 * @param string $data <p>
 * The packed data.
 * </p>
 * @return array an indexed array containing unpacked elements of binary string.
 */
function unpack($format, $data)
{
    return array_values(\unpack($format, $data));
}
