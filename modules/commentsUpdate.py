import string
import re
import logging

import modules.jsdocs as jsdocs

module_logger = logging.getLogger('autoDocBlockr.commentsUpdate')

class CommentsUpdate():
    parser=None
    sublime=None
    view=None

    # Will contain the end result of the doc block
    result=[]

    foundOldDocBlocks=[]

    def __init__(self, mem):
        self.log = logging.getLogger('autoDocBlockr.commentsUpdate.CommentsUpdate')
        self.gc = mem
        self.parser = self.gc.parser
        self.sublime = self.gc
        self.view = self.gc.view
        self.jsDocs = jsdocs.JsdocsCommand(self.gc)
        self.invalidPrefix = mem.settings.get('autoDocBlockr_invalid_prefix')


    def updateComments(self):

        matches=self.gc.matches
        docBlockOut=self.gc.docBlockOut
        self.parsedFuncArgs = self.gc.parsedFuncArgs

        # Parse comments through DocBlockr to use in case there
        # are missing doc blocks
        self.result = []
        self.foundOldDocBlocks = []

        self.jsDocs.initialize(self.sublime.view)
        snippet = self.jsDocs.generateSnippet(docBlockOut)

        self.snippets = string.split(snippet, '\n')
        self.matches = matches

        self.renderNewDocs()

        self.invalidateNotFoundDocs()

        return self.result

    def getDocBloc(self):
        return string.join(self.result, "\n")


    def renderNewDocs(self):
        # Go for each argument found
        for i, v in enumerate(self.parsedFuncArgs):
            # Get the doc block if there's one
            docArg = self.findDocArg(v[1])

            if not docArg:
                newLine=self.getNewDocLine(v[1]).strip()
                #self.log.info("stripped docBlock:" + newLine)
                self.result.append(newLine)
                continue

            # Save the findings
            self.foundOldDocBlocks.append(docArg['seq'])

            # append the doc line
            self.result.append(docArg['line'].strip())

    def invalidateNotFoundDocs(self):
        """See if any old docblocks where not found and invalidate them"""
        #print self.foundOldDocBlocks
        for v in reversed(self.matches):
            if v['seq'] not in self.foundOldDocBlocks:
                self.result.append(re.sub(r'\@param',
                    self.invalidPrefix + 'param',
                    v['line']).strip())

    def findDocArg(self, argument):
        """find a doc block in argument."""
        for v in reversed(self.matches):
            #print "examining argument:" + argument + " with paramName:" + v['paramName']
            if argument == v['paramName']:
                return v
        return None

    def getNewDocLine(self, argument):
        """Find the specified argument in the newly rendered doc block"""

        #first locate the position of the argument

        for i, v in enumerate(self.parsedFuncArgs):
            if argument == v[1]:
                break
        #self.log.info("raw docBlock:" + self.snippets[i+2])
        return self.removeSnippetTags(self.snippets[i + 2])

    def removeSnippetTags(self, string):
        """Return a string without snippet tags"""
        noSnippets = re.sub(r"(\$\{[\d]+\:)(\[[\w]+\])(\})", r"\2", string)
        noSnippets = re.sub(r'\\(.)', r'\1', noSnippets)
        return noSnippets


