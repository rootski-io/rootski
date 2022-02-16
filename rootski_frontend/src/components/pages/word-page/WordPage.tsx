import React, { useEffect } from "react";
import {
  CircularProgress,
  makeStyles,
  Theme,
  Container,
  Typography,
} from "@material-ui/core";
import {
  Word,
  SubDefinition,
  Definition,
  GroupedDefinitions,
  Morpheme,
} from "../../../models/models";
import Breakdown from "../../breakdown/Breakdown";
import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";

import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";

import Grid, { GridSpacing } from "@material-ui/core/Grid";
import Paper from "@material-ui/core/Paper";
import Divider from "@material-ui/core/Divider";
import {
  ExampleSentence,
  NounDeclensions,
  AdjectiveForms,
} from "../../../models/models";

import ExitToAppIcon from "@material-ui/icons/ExitToApp";
import Button from "@material-ui/core/Button";

import Table from "@material-ui/core/Table";
import TableBody from "@material-ui/core/TableBody";
import TableCell from "@material-ui/core/TableCell";
import TableContainer from "@material-ui/core/TableContainer";
import TableHead from "@material-ui/core/TableHead";
import TableRow from "@material-ui/core/TableRow";
import { VerbConjugations, WordType } from "../../../models/models";

// for fetching the word data on load
import { AppState } from "../../../redux/reducers/index";
import { useSelector, shallowEqual, useDispatch } from "react-redux";
import { MorphemeSection } from "./MorphemeSection";
import { WordPageSection } from "./WordPageSection";
import { DefinitionsList } from "./DefinitionsList";

export interface WordPageProps {}

const useStyles = makeStyles((theme: Theme) => ({
  sectionHeading: {
    marginTop: "2rem",
  },
  // hide the bottom border of TableCell's
  noBottomBorder: {
    borderBottom: "none",
  },
  loadingSpinner: {
    // textAlign: "center",
    fontSize: "64px",
    marginTop: "60px",
    marginLeft: "40%",
  },
}));

const WordPage = (props: WordPageProps) => {
  // redux state
  const selectReduxData = (state: AppState) => ({
    loading: state.wordData.loading,
    wordData: state.wordData.wordData,
  });
  const reduxData = useSelector(selectReduxData, shallowEqual);

  // styles
  const classes = useStyles();

  // =====================
  // |     RENDERING     |
  // =====================

  const renderDefinitions = () => {
    if (
      reduxData &&
      reduxData.wordData &&
      reduxData.wordData.word &&
      reduxData.wordData.word.word
    ) {
      return <></>;
    } else {
      return null;
    }
  };

  const renderExamples = (examples: Array<ExampleSentence>) => {
    return (
      <>
        <Typography
          color="primary"
          variant="h5"
          className={classes.sectionHeading}
        >
          Examples
        </Typography>
        <Card>
          <CardContent>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell className={classes.noBottomBorder}>
                    <Typography color="primary">Russian</Typography>
                  </TableCell>
                  <TableCell className={classes.noBottomBorder}>
                    <Typography color="primary">English</Typography>
                  </TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {examples.map((example: ExampleSentence) => {
                  return (
                    <TableRow>
                      <TableCell className={classes.noBottomBorder}>
                        {example.rus}
                      </TableCell>
                      <TableCell className={classes.noBottomBorder}>
                        {example.eng}
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </>
    );
  };

  const renderNounDeclensions = (declensions: NounDeclensions) => {
    return (
      <>
        <Typography
          color="primary"
          variant="h5"
          className={classes.sectionHeading}
        >
          Cases
        </Typography>
        <Card>
          <CardContent>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell className={classes.noBottomBorder}></TableCell>
                  <TableCell className={classes.noBottomBorder}>
                    <Typography color="primary">Singular</Typography>
                  </TableCell>
                  <TableCell className={classes.noBottomBorder}>
                    <Typography color="primary">Plural</Typography>
                  </TableCell>
                </TableRow>
              </TableHead>

              <TableBody>
                <TableRow>
                  <TableCell className={classes.noBottomBorder}>
                    <Typography color="primary">Nominative</Typography>
                  </TableCell>
                  <TableCell className={classes.noBottomBorder}>
                    {declensions.nom}
                  </TableCell>
                  <TableCell className={classes.noBottomBorder}>
                    {declensions.nom_pl}
                  </TableCell>
                </TableRow>

                <TableRow>
                  <TableCell className={classes.noBottomBorder}>
                    <Typography color="primary">Accusative</Typography>
                  </TableCell>
                  <TableCell className={classes.noBottomBorder}>
                    {declensions.acc}
                  </TableCell>
                  <TableCell className={classes.noBottomBorder}>
                    {declensions.acc_pl}
                  </TableCell>
                </TableRow>

                <TableRow>
                  <TableCell className={classes.noBottomBorder}>
                    <Typography color="primary">Genetive</Typography>
                  </TableCell>
                  <TableCell className={classes.noBottomBorder}>
                    {declensions.gen}
                  </TableCell>
                  <TableCell className={classes.noBottomBorder}>
                    {declensions.gen_pl}
                  </TableCell>
                </TableRow>

                <TableRow>
                  <TableCell className={classes.noBottomBorder}>
                    <Typography color="primary">Prepositional</Typography>
                  </TableCell>
                  <TableCell className={classes.noBottomBorder}>
                    {declensions.prep}
                  </TableCell>
                  <TableCell className={classes.noBottomBorder}>
                    {declensions.prep_pl}
                  </TableCell>
                </TableRow>

                <TableRow>
                  <TableCell className={classes.noBottomBorder}>
                    <Typography color="primary">Dative</Typography>
                  </TableCell>
                  <TableCell className={classes.noBottomBorder}>
                    {declensions.dat}
                  </TableCell>
                  <TableCell className={classes.noBottomBorder}>
                    {declensions.dat_pl}
                  </TableCell>
                </TableRow>

                <TableRow>
                  <TableCell className={classes.noBottomBorder}>
                    <Typography color="primary">Instrumental</Typography>
                  </TableCell>
                  <TableCell className={classes.noBottomBorder}>
                    {declensions.inst}
                  </TableCell>
                  <TableCell className={classes.noBottomBorder}>
                    {declensions.inst_pl}
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </>
    );
  };

  const renderAdjectiveForms = (shortForms: AdjectiveForms) => {
    return (
      <>
        <Typography
          color="primary"
          variant="h5"
          className={classes.sectionHeading}
        >
          Short Forms
        </Typography>
        <Card>
          <CardContent>
            <Table size="small">
              <TableBody>
                <TableRow>
                  <TableCell className={classes.noBottomBorder}>
                    <Typography color="primary">Comparative</Typography>
                  </TableCell>
                  <TableCell className={classes.noBottomBorder}>
                    {shortForms.comp}
                  </TableCell>
                </TableRow>

                <TableRow>
                  <TableCell className={classes.noBottomBorder}>
                    <Typography color="primary">Masculine</Typography>
                  </TableCell>
                  <TableCell className={classes.noBottomBorder}>
                    {shortForms.masc_short}
                  </TableCell>
                </TableRow>

                <TableRow>
                  <TableCell className={classes.noBottomBorder}>
                    <Typography color="primary">Neuter</Typography>
                  </TableCell>
                  <TableCell className={classes.noBottomBorder}>
                    {shortForms.neut_short}
                  </TableCell>
                </TableRow>

                <TableRow>
                  <TableCell className={classes.noBottomBorder}>
                    <Typography color="primary">Femenine</Typography>
                  </TableCell>
                  <TableCell className={classes.noBottomBorder}>
                    {shortForms.fem_short}
                  </TableCell>
                </TableRow>

                <TableRow>
                  <TableCell className={classes.noBottomBorder}>
                    <Typography color="primary">Plural</Typography>
                  </TableCell>
                  <TableCell className={classes.noBottomBorder}>
                    {shortForms.plural_short}
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </>
    );
  };

  const renderVerbConjugations = (conjugations: VerbConjugations) => {
    // helper function to derive verb tense from case
    const getVerbTense = (aspect: string) => {
      switch (aspect) {
        case "impf":
          return "Present";
        case "perf":
          return "Future";
        default:
          return "Present/Future";
      }
    };

    const participleOrNA = (str: string) => {
      return str ? str : "N/A";
    };

    return (
      <>
        <Typography
          color="primary"
          variant="h5"
          className={classes.sectionHeading}
        >
          Conjugations
        </Typography>
        <Card>
          {/* Present/Future Conjugations Table */}
          <CardContent>
            <Typography color="primary" variant="h6">
              {getVerbTense(conjugations.aspect)} Tense
            </Typography>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell className={classes.noBottomBorder}></TableCell>
                  <TableCell className={classes.noBottomBorder}>
                    <Typography color="primary">Singular</Typography>
                  </TableCell>
                  <TableCell className={classes.noBottomBorder}>
                    <Typography color="primary">Plural</Typography>
                  </TableCell>
                </TableRow>
              </TableHead>

              <TableBody>
                <TableRow>
                  <TableCell className={classes.noBottomBorder}>
                    <Typography color="primary">1st Person</Typography>
                  </TableCell>
                  <TableCell className={classes.noBottomBorder}>
                    я {conjugations["1st_per_sing"]}
                  </TableCell>
                  <TableCell className={classes.noBottomBorder}>
                    мы {conjugations["1st_per_pl"]}
                  </TableCell>
                </TableRow>

                <TableRow>
                  <TableCell className={classes.noBottomBorder}>
                    <Typography color="primary">2nd Person</Typography>
                  </TableCell>
                  <TableCell className={classes.noBottomBorder}>
                    ты {conjugations["2nd_per_sing"]}
                  </TableCell>
                  <TableCell className={classes.noBottomBorder}>
                    вы {conjugations["2nd_per_pl"]}
                  </TableCell>
                </TableRow>

                <TableRow>
                  <TableCell className={classes.noBottomBorder}>
                    <Typography color="primary">3rd Person</Typography>
                  </TableCell>
                  <TableCell className={classes.noBottomBorder}>
                    он {conjugations["3rd_per_sing"]}
                  </TableCell>
                  <TableCell className={classes.noBottomBorder}>
                    они {conjugations["3rd_per_pl"]}
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </CardContent>

          {/* Past Tense Conjugations Table */}
          <CardContent>
            <Typography color="primary" variant="h6">
              Past Tense
            </Typography>
            <Table size="small">
              <TableBody>
                <TableRow>
                  <TableCell className={classes.noBottomBorder}>
                    <Typography color="primary">
                      {" "}
                      {/* Trick to fix the column spacing for the table */}
                      Masculine {"\xa0\xa0\xa0\xa0 `"}
                    </Typography>
                  </TableCell>
                  <TableCell className={classes.noBottomBorder}>
                    {conjugations.past_m}
                  </TableCell>
                </TableRow>

                <TableRow>
                  <TableCell className={classes.noBottomBorder}>
                    <Typography color="primary">Neuter </Typography>
                  </TableCell>
                  <TableCell className={classes.noBottomBorder}>
                    {conjugations.past_n}
                  </TableCell>
                </TableRow>

                <TableRow>
                  <TableCell className={classes.noBottomBorder}>
                    <Typography color="primary">Femenine </Typography>
                  </TableCell>
                  <TableCell className={classes.noBottomBorder}>
                    {conjugations.past_f}
                  </TableCell>
                </TableRow>

                <TableRow>
                  <TableCell className={classes.noBottomBorder}>
                    <Typography color="primary">Plural</Typography>
                  </TableCell>
                  <TableCell className={classes.noBottomBorder}>
                    {conjugations.past_pl}
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </CardContent>

          {/* Participle Table */}
          <CardContent>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell className={classes.noBottomBorder}></TableCell>
                  <TableCell className={classes.noBottomBorder}>
                    <Typography color="primary">Active</Typography>
                  </TableCell>
                  <TableCell className={classes.noBottomBorder}>
                    <Typography color="primary">Passive</Typography>
                  </TableCell>
                </TableRow>
              </TableHead>

              <TableBody>
                <TableRow>
                  <TableCell className={classes.noBottomBorder}>
                    <Typography color="primary">
                      {getVerbTense(conjugations.aspect)}
                    </Typography>
                  </TableCell>
                  <TableCell className={classes.noBottomBorder}>
                    {participleOrNA(conjugations.actv_part)}
                  </TableCell>
                  <TableCell className={classes.noBottomBorder}>
                    {participleOrNA(conjugations.pass_part)}
                  </TableCell>
                </TableRow>

                <TableRow>
                  <TableCell className={classes.noBottomBorder}>
                    <Typography color="primary">Past</Typography>
                  </TableCell>
                  <TableCell className={classes.noBottomBorder}>
                    {participleOrNA(conjugations.actv_past_part)}
                  </TableCell>
                  <TableCell className={classes.noBottomBorder}>
                    {participleOrNA(conjugations.pass_past_part)}
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </CardContent>

          {/* Imperative and Gerund Table */}
          <CardContent>
            <Table size="small">
              <TableBody>
                <TableRow>
                  <TableCell className={classes.noBottomBorder}>
                    <Typography color="primary">Imperative Singular</Typography>
                  </TableCell>
                  <TableCell className={classes.noBottomBorder}>
                    {conjugations.impr}
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell className={classes.noBottomBorder}>
                    <Typography color="primary">Imperative Plural</Typography>
                  </TableCell>
                  <TableCell className={classes.noBottomBorder}>
                    {conjugations.impr_pl}
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell className={classes.noBottomBorder}>
                    <Typography color="primary">Gerund</Typography>
                  </TableCell>
                  <TableCell className={classes.noBottomBorder}>
                    {conjugations.gerund}
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </>
    );
  };

  // ===============================
  // |   LOGIC / EVENT HANDLERS    |
  // ===============================

  const [editBreakdownMode, setEditBreakdownMode] = React.useState(false);

  // transform definitions
  if (reduxData.loading) {
    return <CircularProgress className={classes.loadingSpinner} size={100} />;
  } else if (reduxData.wordData != null) {
    return (
      <Container maxWidth="md">
        {/* <p>
          TODO: (1) display wordData.aspectual pairs (2) space out tables (3)
          make text bigger/better font (4) make search results use browser
          router links, and have WordPage component actually trigger the API
          request, so that the web app will work with hyper links (5) use
          prettier rendering logic for the various word page sections
        </p> */}
        {/* <p>{JSON.stringify(reduxData.wordData)}!!!</p> */}

        <Breakdown
          breakdown={reduxData.wordData.breakdown}
          word={reduxData.wordData.word}
          editBreakdownMode={editBreakdownMode}
          setEditBreakdownMode={setEditBreakdownMode}
        />

        {/* Morphemes */}
        {!editBreakdownMode &&
        reduxData.wordData.breakdown !== null &&
        reduxData.wordData.breakdown.breakdown_items.filter(
          (m: Morpheme) => m.type !== null
        ).length > 0 ? (
          <MorphemeSection
            breakdown={reduxData.wordData.breakdown}
            sectionHeadingClassName={classes.sectionHeading}
          />
        ) : null}

        {/* Definitions */}
        {reduxData && reduxData.wordData && reduxData.wordData.definitions ? (
          <DefinitionsList
            word={reduxData.wordData.word.word}
            definitions={reduxData.wordData.definitions}
          />
        ) : null}

        {/* Examples */}
        {reduxData.wordData &&
        reduxData.wordData.sentences &&
        reduxData.wordData.sentences.length > 0 ? (
          renderExamples(reduxData.wordData.sentences)
        ) : (
          <Typography
            color="primary"
            variant="h5"
            className={classes.sectionHeading}
          >
            No Examples
          </Typography>
        )}

        {/* Noun Cases */}
        {reduxData.wordData && reduxData.wordData.declensions
          ? renderNounDeclensions(reduxData.wordData.declensions)
          : null}

        {/* Adj. Short Forms */}
        {reduxData.wordData && reduxData.wordData.short_forms
          ? renderAdjectiveForms(reduxData.wordData.short_forms)
          : null}

        {/* Adj. Short Forms */}
        {reduxData.wordData && reduxData.wordData.conjugations
          ? renderVerbConjugations(reduxData.wordData.conjugations)
          : null}

        {/* Lots of blank lines for a satisfying scroll experience :D */}
        {[...Array(15)].map(() => (
          <br />
        ))}
      </Container>
    );
  } else {
    return null;
  }
};

export default WordPage;
