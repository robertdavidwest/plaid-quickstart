import React, { useContext } from "react";
import Button from "plaid-threads/Button";
import Context from "../../Context";
import { AUTH_TOKEN }  from "../../constants";


function Logout() {
  const { dispatch } = useContext(Context);

  const handleClick = () => {
    dispatch({ type: "SET_STATE", state: { isLoggedIn: false } });
    dispatch({ type: "SET_STATE", state: { authToken: null } });
    dispatch({ type: "SET_STATE", state: { userId: null } });
    window.localStorage.removeItem(AUTH_TOKEN);
  }
  return (
    <div>
      <Button type="button" large onClick={handleClick}>Logout</Button>
    </div>
  );
}

Logout.displayName = "Logout";

export default Logout;
