import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react";
import {
  browserLocalPersistence,
  browserSessionPersistence,
  createUserWithEmailAndPassword,
  onAuthStateChanged,
  sendPasswordResetEmail,
  setPersistence,
  signInWithEmailAndPassword,
  signOut,
  updateProfile,
} from "firebase/auth";
import { doc, getDoc, serverTimestamp, setDoc } from "firebase/firestore";
import { auth, db } from "../firebase";

const OneContext = createContext(null);

const DEFAULT_FAVORITES = [
  "amazon-shopping",
  "prime-video",
  "aws",
  "amazon-pay",
];
const DEFAULT_RECENTS = ["prime-video", "amazon-shopping", "alexa-echo"];
const DEFAULT_INTERESTS = ["Shopping", "Entertainment", "Cloud", "Devices"];
const DEFAULT_AVATAR =
  "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=200&q=80";

function profileRef(uid) {
  return doc(db, "users", uid);
}

function getFriendlyAuthError(error) {
  const messages = {
    "auth/invalid-credential": "Email or password is incorrect.",
    "auth/invalid-email": "Please enter a valid email address.",
    "auth/user-not-found":
      "No account exists for this email. Create an account first.",
    "auth/wrong-password": "Email or password is incorrect.",
    "auth/email-already-in-use":
      "An account already exists for this email. Please sign in.",
    "auth/weak-password": "Choose a password with at least 6 characters.",
    "auth/too-many-requests": "Too many attempts. Please wait and try again.",
    "auth/network-request-failed":
      "Network error. Check your internet connection.",
    "auth/operation-not-allowed":
      "Email/Password sign-in is not enabled in Firebase Authentication.",
  };

  return (
    messages[error?.code] ||
    error?.message ||
    "Something went wrong. Please try again."
  );
}

export function OneProvider({ children }) {
  const [favorites, setFavorites] = useState(DEFAULT_FAVORITES);
  const [recentlyVisited, setRecentlyVisited] = useState(DEFAULT_RECENTS);
  const [userInterests, setUserInterests] = useState(DEFAULT_INTERESTS);
  const [cart, setCart] = useState([]);
  const [settings, setSettings] = useState({});
  const [currentUser, setCurrentUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [toast, setToast] = useState(null);
  const hydratedUid = useRef(null);

  const showToast = useCallback((message, type = "info") => {
    setToast({ message, type, id: Date.now() });
    window.setTimeout(() => setToast(null), 3200);
  }, []);

  const applyUserData = useCallback((profile = {}) => {
    setFavorites(
      Array.isArray(profile.favorites) ? profile.favorites : DEFAULT_FAVORITES
    );
    setRecentlyVisited(
      Array.isArray(profile.recentlyVisited)
        ? profile.recentlyVisited
        : DEFAULT_RECENTS
    );
    setUserInterests(
      Array.isArray(profile.userInterests)
        ? profile.userInterests
        : DEFAULT_INTERESTS
    );
    setCart(Array.isArray(profile.cart) ? profile.cart : []);
    setSettings(
      profile.settings &&
        typeof profile.settings === "object" &&
        !Array.isArray(profile.settings)
        ? profile.settings
        : {}
    );
  }, []);

  useEffect(() => {
    let active = true;

    const unsubscribe = onAuthStateChanged(
      auth,
      async (user) => {
        if (!active) return;

        hydratedUid.current = null;
        setAuthLoading(true);

        if (!user) {
          setCurrentUser(null);
          applyUserData();
          setAuthLoading(false);
          return;
        }

        try {
          const snapshot = await getDoc(profileRef(user.uid));
          if (!active) return;

          const profile = snapshot.exists() ? snapshot.data() : {};
          applyUserData(profile);
          setCurrentUser({
            uid: user.uid,
            name: profile.name || user.displayName || user.email || "Amazon One member",
            email: user.email || "",
            avatar: profile.avatar || user.photoURL || DEFAULT_AVATAR,
            membershipTier: profile.membershipTier || "Prime",
            isLoggedIn: true,
          });
          hydratedUid.current = user.uid;
        } catch {
          if (!active) return;

          setCurrentUser({
            uid: user.uid,
            name: user.displayName || user.email || "Amazon One member",
            email: user.email || "",
            avatar: user.photoURL || DEFAULT_AVATAR,
            membershipTier: "Prime",
            isLoggedIn: true,
          });
          showToast(
            "Your account is signed in, but its saved profile could not be loaded.",
            "warning"
          );
        } finally {
          if (active) setAuthLoading(false);
        }
      },
      (error) => {
        if (!active) return;
        setAuthLoading(false);
        showToast(getFriendlyAuthError(error), "warning");
      }
    );

    return () => {
      active = false;
      unsubscribe();
    };
  }, [applyUserData, showToast]);

  useEffect(() => {
    const uid = currentUser?.uid;
    if (!uid || hydratedUid.current !== uid) return;

    setDoc(
      profileRef(uid),
      {
        favorites,
        recentlyVisited,
        userInterests,
        cart,
        settings,
        updatedAt: serverTimestamp(),
      },
      { merge: true }
    ).catch(() => {
      showToast("Your profile changes could not be saved.", "warning");
    });
  }, [
    cart,
    currentUser,
    favorites,
    recentlyVisited,
    settings,
    showToast,
    userInterests,
  ]);

  const login = useCallback(
    async (email, password, keepSignedIn = true) => {
      try {
        await setPersistence(
          auth,
          keepSignedIn ? browserLocalPersistence : browserSessionPersistence
        );
        const credential = await signInWithEmailAndPassword(
          auth,
          email.trim(),
          password
        );
        showToast("Welcome back!", "success");
        return credential.user;
      } catch (error) {
        showToast(getFriendlyAuthError(error), "warning");
        throw error;
      }
    },
    [showToast]
  );

  const register = useCallback(
    async ({ name, email, password }) => {
      try {
        const credential = await createUserWithEmailAndPassword(
          auth,
          email.trim(),
          password
        );
        const cleanName = name.trim();
        await updateProfile(credential.user, { displayName: cleanName });
        await setDoc(profileRef(credential.user.uid), {
          name: cleanName,
          email: credential.user.email,
          avatar: DEFAULT_AVATAR,
          membershipTier: "Prime",
          favorites: DEFAULT_FAVORITES,
          recentlyVisited: DEFAULT_RECENTS,
          userInterests: DEFAULT_INTERESTS,
          cart: [],
          settings: {},
          createdAt: serverTimestamp(),
          updatedAt: serverTimestamp(),
        });
        showToast(`Welcome, ${cleanName}!`, "success");
        return credential.user;
      } catch (error) {
        showToast(getFriendlyAuthError(error), "warning");
        throw error;
      }
    },
    [showToast]
  );

  const resetPassword = useCallback(
    async (email) => {
      try {
        await sendPasswordResetEmail(auth, email.trim());
        showToast("Password reset email sent.", "success");
      } catch (error) {
        showToast(getFriendlyAuthError(error), "warning");
        throw error;
      }
    },
    [showToast]
  );

  const logout = useCallback(async () => {
    try {
      await signOut(auth);
      showToast("You have been signed out.", "info");
    } catch (error) {
      showToast(getFriendlyAuthError(error), "warning");
      throw error;
    }
  }, [showToast]);

  const toggleFavorite = useCallback(
    (serviceId) => {
      setFavorites((previous) => {
        const isFavorite = previous.includes(serviceId);
        showToast(
          isFavorite ? "Removed from Favorites" : "Saved to My Favorites!",
          "success"
        );
        return isFavorite
          ? previous.filter((id) => id !== serviceId)
          : [...previous, serviceId];
      });
    },
    [showToast]
  );

  const recordVisit = useCallback((serviceId) => {
    setRecentlyVisited((previous) => [
      serviceId,
      ...previous.filter((id) => id !== serviceId),
    ].slice(0, 6));
  }, []);

  const addToCart = useCallback(
    (product) => {
      setCart((previous) => {
        const existing = previous.find((item) => item.id === product.id);
        if (existing) {
          showToast(`Increased quantity for ${product.name}`, "info");
          return previous.map((item) =>
            item.id === product.id ? { ...item, qty: item.qty + 1 } : item
          );
        }
        showToast(`Added "${product.name}" to Demo Cart!`, "success");
        return [...previous, { ...product, qty: 1 }];
      });
    },
    [showToast]
  );

  const removeFromCart = useCallback(
    (productId) => {
      setCart((previous) => previous.filter((item) => item.id !== productId));
      showToast("Item removed from cart", "info");
    },
    [showToast]
  );

  const clearCart = useCallback(() => {
    setCart([]);
    showToast("Cart cleared", "info");
  }, [showToast]);

  return (
    <OneContext.Provider
      value={{
        favorites,
        toggleFavorite,
        recentlyVisited,
        recordVisit,
        userInterests,
        setUserInterests,
        settings,
        setSettings,
        currentUser,
        authLoading,
        login,
        register,
        resetPassword,
        logout,
        cart,
        addToCart,
        removeFromCart,
        clearCart,
        toast,
        showToast,
      }}
    >
      {children}
    </OneContext.Provider>
  );
}

export function useOne() {
  const context = useContext(OneContext);
  if (!context) throw new Error("useOne must be used within a OneProvider");
  return context;
}
