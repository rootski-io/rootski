import React from "react";
import { WordPageSection } from "./WordPageSection";
import {
  Definition,
  GroupedDefinitions,
  SubDefinition,
} from "../../../models/models";
import Button from "@material-ui/core/Button";
import ExitToAppIcon from "@material-ui/icons/ExitToApp";

import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import ListItemText from "@material-ui/core/ListItemText";
import ListSubheader from "@material-ui/core/ListSubheader";
import { Typography, Theme } from "@material-ui/core";
import { makeStyles } from "@material-ui/core/styles";

const useStyles = makeStyles((theme: Theme) => ({
  definitionLink: {
    marginRight: "0.5rem",
    marginBottom: "0.5rem",
  },
}));

/**
 * Concatenate all sub definitions in the given definition
 *
 * @return "sub_def1 (notes1); sub_def2 (notes2); ..."
 */
const getDefinitionText = (def: Definition) => {
  let definition_text = "";

  // concatenate all the subdefs and notes together
  let sub_def_strings: Array<string> = def.sub_defs.map(
    (sub_def: SubDefinition) => {
      const notes = sub_def.notes ? " " + sub_def.notes : "";
      return sub_def.definition + notes;
    }
  );
  definition_text += sub_def_strings.join("; ");

  return definition_text;
};

const renderDefinitionGroups = (definitions: Array<GroupedDefinitions>) => {
  return (
    <>
      {definitions.map((defGroup: GroupedDefinitions) => {
        return (
          <List
            subheader={
              <ListSubheader>
                <Typography color="primary" variant="h6">
                  {defGroup.word_type}
                </Typography>
              </ListSubheader>
            }
          >
            {defGroup.definitions.map((def: Definition, index: number) => {
              const defText = `(${index + 1}) ${getDefinitionText(def)}`;
              return (
                <ListItem>
                  <ListItemText primary={defText} />
                </ListItem>
              );
            })}
          </List>
        );
      })}
    </>
  );
};

interface DefinitionsListProps {
  word: string;
  definitions: Array<GroupedDefinitions>;
}

export const DefinitionsList = (props: DefinitionsListProps) => {
  const { word, definitions } = props;
  const glosbeLink = `https://glosbe.com/ru/en/${word}`;
  const wordReferenceLink = `https://www.wordreference.com/ruen/${word}`;
  const reversoLink = `https://dictionary.reverso.net/russian-english/${word}`;
  const ponsLink = `https://en.pons.com/translate/russian-english/${word}`;
  const lingueeLink = `https://www.linguee.com/russian-english/translation/${word}.html`;

  const classes = useStyles();

  return (
    <>
      <WordPageSection title={"Definitions"}>
        <Button
          variant="outlined"
          color="primary"
          startIcon={<ExitToAppIcon />}
          className={classes.definitionLink}
          href={glosbeLink}
          target="_blank"
        >
          glosbe
        </Button>
        <Button
          variant="outlined"
          color="primary"
          startIcon={<ExitToAppIcon />}
          href={wordReferenceLink}
          className={classes.definitionLink}
          target="_blank"
        >
          Word Reference
        </Button>
        <Button
          variant="outlined"
          color="primary"
          startIcon={<ExitToAppIcon />}
          href={reversoLink}
          className={classes.definitionLink}
          target="_blank"
        >
          Reverso
        </Button>
        <Button
          variant="outlined"
          color="primary"
          startIcon={<ExitToAppIcon />}
          className={classes.definitionLink}
          href={ponsLink}
          target="_blank"
        >
          pons
        </Button>
        <Button
          variant="outlined"
          color="primary"
          startIcon={<ExitToAppIcon />}
          className={classes.definitionLink}
          href={lingueeLink}
          target="_blank"
        >
          linguee
        </Button>
        {definitions ? renderDefinitionGroups(definitions) : null}
      </WordPageSection>
    </>
  );
};
