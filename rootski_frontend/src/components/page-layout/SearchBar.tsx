/**
 *
 * A beautiful Search Bar created with the MaterialUI Autocomplete.
 * It consists of a SearchIcon and Autocomplete contained inside of
 * a button. It is wired up to the redux search reducer.
 *
 * There is also a Snack Bar for popping error toasts whenever you enter
 * something invalid in the search bar
 *
 */

import React from "react";
import TextField from "@material-ui/core/TextField";
import Button from "@material-ui/core/Button";
import Autocomplete, {
  createFilterOptions,
} from "@material-ui/lab/Autocomplete";
import {
  CircularProgress,
  makeStyles,
  Theme,
  Snackbar,
  Slide,
  Typography,
} from "@material-ui/core";
import { useSelector, shallowEqual, useDispatch } from "react-redux";
import { AppState } from "../../redux/reducers";
import { Word } from "../../models/models";
import SearchIcon from "@material-ui/icons/Search";
import MuiAlert, { AlertProps } from "@material-ui/lab/Alert";
import { TransitionProps } from "@material-ui/core/transitions/transition";
import { Link, Switch, useHistory } from "react-router-dom";
import { searchAction, updateLoading } from "../../redux/actions/SearchActions";

// constants
const LOADING_OPTION_TEXT = "Loading...";
const NO_RESULTS_OPTION_TEXT = "No results";
const ALERT_DURATION = 7000; // milliseconds
const VALID_SEARCH_PATTERN = /[A-z0-9А-яЁё \-]*/; // roman and cyrillic alphanumeric, space, hyphen

const NO_PENDING_SEARCH_TIMEOUT = 0;
const SEARCH_DELAY_TIME = 650; // in milliseconds

const filter = createFilterOptions({
  matchFrom: "start",
  // stringify builds a search key from an object.
  // We can call filter(wordObject), which would parse out the searchKey i.e. wordObject.word
  // and run it against all the other words in the options list
  stringify: (word: Word) => word.word,
});

const useStyles = makeStyles((theme: Theme) => ({
  listItemTag: {
    marginLeft: "15px",
  },
  searchIcon: {
    marginRight: "8px",
    marginTop: "10px",
    marginLeft: "3px",
    marginBottom: "7px",
  },
  spinner: { position: "absolute", right: "45px" },
  closeIcon: { marginRight: "20px", position: "absolute", right: 20 },
  searchBarContainer: {
    margin: "10px",
    minWidth: "500px",
    borderRadius: 2.5,
    textTransform: "none",
    "&:hover": {
      backgroundColor: "white",
    },
    [theme.breakpoints.down("md")]: {
      minWidth: "500px",
    },
    [theme.breakpoints.down("sm")]: {
      minWidth: "450px",
    },
  },
  searchInput: {
    borderRadius: 2.5,
    [theme.breakpoints.down("md")]: {
      width: "500px",
    },
    [theme.breakpoints.down("sm")]: {
      width: "100%",
    },
    "&:hover": {
      backgroundColor: "white",
    },
    "&:not(:hover)": {
      backgroundColor: "white",
    },
  },
  searchResultsBox: {
    zIndex: 1000,
  },
  alert: {
    minWidth: "400px",
    zIndex: 2000,
  },
}));

const SearchBar = () => {
  // hooks
  const classes = useStyles();
  const browserHistory = useHistory();

  // state
  const [inputValue, setInputValue] = React.useState<Word | null>(null); // later type Word, currently selected word
  const [showAlert, setShowAlert] = React.useState<boolean>(false);
  const [typingTimeout, setTypingTimeout] = React.useState<number>(
    NO_PENDING_SEARCH_TIMEOUT
  );

  // redux actions
  const dispatch = useDispatch();
  const search = searchAction(dispatch); // creates a search action function

  // redux state
  const selectReduxData = (state: AppState) => ({
    loading: state.search.loading,
    matchedWords: state.search.matchedWords,
  });
  const reduxData = useSelector(selectReduxData, shallowEqual);

  // =====================
  // |     RENDERING     |
  // =====================

  // option should be of type Word
  const renderOption = (option: Word) => {
    // show the tag if not loading or no results
    const showTag = ![LOADING_OPTION_TEXT, NO_RESULTS_OPTION_TEXT].includes(
      option.word
    );

    // @ts-ignore
    return (
      <>
        {option.word}
        {""}
        {showTag ? (
          <Button
            color="primary"
            variant="contained"
            size="small"
            className={classes.listItemTag}
          >
            Word
          </Button>
        ) : null}
      </>
    );
  };

  const renderInput = (params: any) => {
    return (
      <div className={classes.searchBarContainer}>
        <TextField
          {...params}
          autoFocus={false}
          fullWidth
          variant="outlined"
          placeholder="Search roots, words, study sets..."
          className={classes.searchInput}
          color="secondary"
          // @ts-ignore
          InputProps={{
            ...params.InputProps,
            type: "search",
            onChange: onSearchTextChanged,
            className: classes.searchInput,
            startAdornment: <SearchIcon className={classes.searchIcon} />,
            endAdornment: (
              <>
                {reduxData.loading ? (
                  <CircularProgress
                    color="inherit"
                    size={20}
                    className={classes.spinner}
                  />
                ) : null}
              </>
            ),
          }}
        />
      </div>
    );
  };

  // ===============================
  // |   LOGIC / EVENT HANDLERS    |
  // ===============================

  /**
   * Called whenever an option from the drop down is selected
   * @param event Sometimes MouseEvent, sometimes KeyboardEvent, maybe others
   * @param selectedOption Word object chosen by event
   */
  const onOptionSelected = (event: any, selectedOption: Word | null) => {
    setInputValue(selectedOption);

    // navigate to the word page!
    if (selectedOption) {
      const wordPageUrl = `/word/${selectedOption.word_id}/${selectedOption.pos}`;
      browserHistory.push(wordPageUrl);
    }
  };

  /**
   *
   * @param options Available options to choose from
   * @param state The state of the component, of form { inputValue: string }
   */
  const filterOptionsToShow = (options: Array<Word>, state: any) => {
    const filtered = filter(options, state) as Word[];

    // show a list item of "Loading..." or "No results"
    if (state.inputValue !== "" && reduxData.loading) {
      const loadingWord: Word = {
        word_id: -1,
        frequency: -1,
        word: LOADING_OPTION_TEXT,
        pos: null,
      };
      filtered.push(loadingWord);
    } else if (state.inputValue !== "" && filtered.length === 0) {
      const noResultsWord: Word = {
        word_id: -1,
        frequency: -1,
        word: NO_RESULTS_OPTION_TEXT,
        pos: null,
      };
      filtered.push(noResultsWord);
    }

    return filtered;
  };

  // pass option as type Word later
  const getOptionLabel = (wordOption: Word) => {
    return wordOption.word;
  };

  /**
   * Option is disabled if "Loading" or "No results"
   */
  const getOptionDisabled = (option: Word) => {
    return [LOADING_OPTION_TEXT, NO_RESULTS_OPTION_TEXT].includes(option.word);
  };

  const scheduleSearch = (searchText: string) => {
    if (typingTimeout !== NO_PENDING_SEARCH_TIMEOUT) {
      dispatch(updateLoading(false)); // stop loading
      clearTimeout(typingTimeout); // cancel pending search
    }
    // @ts-ignore
    setTypingTimeout(setTimeout(() => search(searchText), SEARCH_DELAY_TIME));
  };

  /**
   * Send a new search request every time the search bar text changes
   * @param event
   */
  const onSearchTextChanged = (event: React.ChangeEvent<HTMLInputElement>) => {
    const searchText = event.target.value;

    // validate search
    if (
      VALID_SEARCH_PATTERN.test(searchText) && // are there any pattern matches?
      // @ts-ignore
      searchText.match(VALID_SEARCH_PATTERN)[0] && // did regex have a match on the first character?
      // @ts-ignore
      searchText.match(VALID_SEARCH_PATTERN)[0] === searchText // is that match the whole searchText?
    ) {
      setShowAlert(false);
      scheduleSearch(searchText);
    } else if (searchText != "") {
      setShowAlert(true);
    }
  };

  // alert
  const onCloseAlert = () => {
    setShowAlert(false);
  };

  return (
    <>
      <Autocomplete
        // ListboxComponent
        value={inputValue}
        onChange={onOptionSelected}
        filterOptions={filterOptionsToShow}
        getOptionDisabled={getOptionDisabled}
        options={reduxData.matchedWords}
        getOptionLabel={getOptionLabel}
        renderOption={renderOption}
        renderInput={renderInput}
        // disableClearable
        loading
      />

      <Snackbar
        onClick={onCloseAlert}
        className={classes.alert}
        autoHideDuration={ALERT_DURATION}
        open={showAlert}
        onClose={onCloseAlert}
        anchorOrigin={{
          vertical: "bottom",
          horizontal: "center",
        }}
        TransitionComponent={(props: TransitionProps) => (
          <Slide {...props} direction="down" />
        )}
      >
        <MuiAlert
          className={classes.alert}
          elevation={20}
          variant="standard"
          severity="error"
          action={
            <Button onClick={onCloseAlert} variant="text" color="secondary">
              Yes, Ma'am!
            </Button>
          }
        >
          Don't use these characters in search:{" "}
          <Typography variant="overline">(1) ' (2) " (3) , (4) ;</Typography>
        </MuiAlert>
      </Snackbar>
    </>
  );
};

export default SearchBar;
