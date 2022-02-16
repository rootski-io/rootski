import { Theme, createMuiTheme } from "@material-ui/core";
import { blue } from "@material-ui/core/colors";

export const theme: Theme = createMuiTheme({
  palette: {
    primary: {
      main: blue[700],
    },
  },
});
